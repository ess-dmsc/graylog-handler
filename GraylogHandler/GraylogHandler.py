#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
import json
import threading
from queue import Queue, Empty
import time

#----------------------------------------------------------------------
def thread_function(host, port, msg_queue, stat_queue, conf_queue):
	""""Thread function which connects to a Graylog server and sends log
	messages to that server."""
	errorWait = 5.0
	cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	cSocket.settimeout(1.0)
	connected = False
	last_connection = time.time()
	msgBuffer = bytearray()
	try:
		cSocket.connect((host, port))
		stat_queue.put("Connected")
		connected = True
	except (ConnectionRefusedError, socket.gaierror, socket.timeout) as e:
		stat_queue.put("Not connected")
		
	while (True):
		if (not conf_queue.empty()):
			confMsg = conf_queue.get()
			if (confMsg == "exit"):
				break
			else:
				assert False
		if (connected):
			if (len(msgBuffer) > 0):
				try:
					sent = cSocket.send(msgBuffer)
					msgBuffer = msgBuffer[sent:]
				except socket.error as e:
					connected = False
					stat_queue.put("Disconnected")
			else:
				try:
					msgBuffer = msg_queue.get(timeout = 0.5)
				except Empty as e:
					msgBuffer = bytearray()
		else:
			if (last_connection + 5 > time.time()):
				time.sleep(0.5)
			else:
				last_connection = time.time()
				try:
					cSocket.connect((host, port))
					stat_queue.put("Connected")
					connected = True
				except (BlockingIOError, socket.gaierror, TimeoutError, OSError) as e:
					stat_queue.put("Not connected")
	if (connected):
		try:
			cSocket.shutdown(socket.SHUT_RDWR)
		except OSError as e:
			pass
	cSocket.close()
	

########################################################################
class GraylogConnection(object):
	"""Used by GraylogHandler to keep track of connections to Graylog servers.
	Stores messages in a circular buffer of limited length until connection
	is established and the messages are sent to the server. Spawns a thread
	in order to enable connection to multipe Graylog servers."""

	#----------------------------------------------------------------------
	def __init__(self, host, port, queue_len):
		"""Inits the Graylog connection using the provided host and port. The
		length of the message queue is set with queue_len.
		"""
		self.message_queue = Queue()
		self.status_queue = Queue()
		self.conf_queue = Queue()
		self.status_str = "Not connected"
		thread_kwargs = {"host":host, "port":port, "msg_queue":self.message_queue, "stat_queue":self.status_queue, "conf_queue":self.conf_queue}
		self.thread = threading.Thread(target = thread_function, kwargs = thread_kwargs)
		self.thread.daemon = True
		self.thread.start()
	
	#----------------------------------------------------------------------
	def __del__(self):
		"""Destructor. Tells the thread to exit and then waits for it to do so."""
		self.conf_queue.put("exit")
		self.thread.join()
	
	#----------------------------------------------------------------------
	def SendMsg(self, msg):
		"""Simply sends a log message. Tells the thread to exit if the message
		is 'exit'."""
		if (type(msg) == str):
			msg = bytearray(msg.encode("utf-8"))
		self.message_queue.put(msg)
	
	#----------------------------------------------------------------------
	@property
	def status(self):
		"""Returns the connection status."""
		while (not self.status_queue.empty()):
			self.status_str = self.status_queue.get()
		return self.status_str
	
	#----------------------------------------------------------------------
	@property
	def messages_in_queue(self):
		"""Returns the number of messages in the message queue."""
		return self.message_queue.qsize()
		
		
		

########################################################################
class GraylogHandler(logging.Handler):
	"""A Python logging handler which is used to send log messages  to  a
	Graylog server usign the GELF protocol. The handler is set to have a
	buffer of messages in case the graylog server is not available.
	The handler is also hard coded to send messages to a local host and
	two different IP:s used at the ESS which run Graylog servers."""

	#----------------------------------------------------------------------
	def __init__(self, queue_len = 100, servers = None):
		"""Constructor"""
		super(GraylogHandler, self).__init__()
		self.queue_len = queue_len
		if (None == servers):
			self.graylog_servers = [("localhost", 12201), ]
		else:
			self.graylog_servers = servers
		
		self.severity_levels = {50:2, 40:3, 30:4, 20:6, 10:7, 0:2}
		self.connections = []
		self.host = socket.gethostname()
		self.CreateConnections()
	
	#----------------------------------------------------------------------
	def close(self):
		for i in range(len(self.connections)):
			con = self.connections.pop()
			del con
	
	#----------------------------------------------------------------------
	def CreateConnections(self):
		"""Creates the actual connections to the Graylog servers."""
		for cServ in self.graylog_servers:
			if (type(cServ[1]) is not int):
				raise TypeError
			if (type(cServ[0]) is not str):
				raise TypeError
			self.connections.append(GraylogConnection(cServ[0], cServ[1], self.queue_len))
	
	#----------------------------------------------------------------------
	def CreateMessage(self, log_dict):
		"""Creates a JSON struct from the dictionary containing the log message
		and appends a '\0' character at the end."""
		return json.dumps(log_dict).encode("utf-8") + b'\x00'
		
	
	#----------------------------------------------------------------------
	def emit(self, record):
		"""Generates the GELF data that is sent to the Graylog server(s)."""
		log_dict = {}
		log_dict["version"] = "1.1"
		assert record.levelno in self.severity_levels
		log_dict["level"] = self.severity_levels[record.levelno]
		log_dict["short_message"] = record.msg
		log_dict["_process"] = record.processName
		log_dict["_processId"] = record.process
		log_dict["timestamp"] = record.created
		log_dict["host"] = self.host
		log_dict["_threadId"] = record.thread
		msgData = self.CreateMessage(log_dict)
		for server in self.connections:
			server.SendMsg(msgData)
		