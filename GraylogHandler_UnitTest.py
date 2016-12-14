#!/usr/bin/env python
# -*- coding: utf-8 -*-

from GraylogHandler import GraylogHandler, GraylogConnection

import unittest
import time
import socket
import random

########################################################################
class TestGraylogConnection(unittest.TestCase):
	#----------------------------------------------------------------------
	def getPort(self):
		return 15000 + random.randint(0, 5000)
	
	#----------------------------------------------------------------------
	def createServer(self, host, port):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((host, port))
		s.listen(1)
		return s
	
	#----------------------------------------------------------------------
	def testNotConnected(self):
		fake_host = "no_host"
		fake_port = self.getPort()
		gConnection = GraylogConnection(fake_host, fake_port, 100)
		time.sleep(0.5)
		self.assertEqual(gConnection.status, "Not connected", msg = "Connection status is incorrect.")
		del gConnection
	
	#----------------------------------------------------------------------
	def testConnected(self):
		host = "localhost"
		port = self.getPort()	
		s = self.createServer(host, port)
		gConnection = GraylogConnection(host, port, 100)
		conn, addr = s.accept()
		time.sleep(0.5)
		self.assertEqual(gConnection.status, "Connected", msg = "Connection status is incorrect.")
		conn.shutdown(socket.SHUT_RDWR)
		conn.close()
		s.close()
		del gConnection
	
	#----------------------------------------------------------------------
	def testMsg(self):
		host = "localhost"
		port = self.getPort()	
		s = self.createServer(host, port)
		gConnection = GraylogConnection(host, port, 100)
		conn, addr = s.accept()
		test_msg = "abcdefghijklmnopqrstuvwxyz"
		gConnection.SendMsg(test_msg)
		rec_msg = conn.recv(len(test_msg))
		self.assertEqual(test_msg, rec_msg.decode("utf-8"), "Sent and recieved messages are not equal.")
		conn.settimeout(0.5)
		with self.assertRaises(socket.timeout):
			res = conn.recv(1)
		conn.shutdown(socket.SHUT_RDWR)
		conn.close()
		s.close()
		del gConnection
	
	#----------------------------------------------------------------------
	def testDisconnected(self):
		host = "localhost"
		port = self.getPort()
		s = self.createServer(host, port)
		gConnection = GraylogConnection(host, port, 100)
		conn, addr = s.accept()
		test_msg = "test"
		gConnection.SendMsg(test_msg)
		rec_msg = conn.recv(len(test_msg))
		self.assertEqual(test_msg, rec_msg.decode("utf-8"), "Sent and recieved messages are not equal.")
		conn.shutdown(socket.SHUT_RDWR)
		conn.close()
		s.close()
		del conn
		del s
		for i in range(100):
			gConnection.SendMsg(test_msg * 100)
		time.sleep(0.1)
		self.assertEqual(gConnection.status, "Disconnected", "Expected status to be disconnected but it was not.")
		del gConnection
	
	#----------------------------------------------------------------------
	def testQueueLength(self):
		host = "no_host"
		port = self.getPort()
		gConnection = GraylogConnection(host, port, 100)
		self.assertEqual(gConnection.messages_in_queue, 0, "Expected 0 messages in queue. This was not the case.")
		gConnection.SendMsg("test")
		time.sleep(0.1)
		self.assertEqual(gConnection.messages_in_queue, 1, "Expected 1 message in queue. This was not the case.")

########################################################################
class TestGraylogHandler(unittest.TestCase):
	#----------------------------------------------------------------------
	def testDefaultServerCreation(self):
		server_list = (("localhost", 12201), ("10.4.0.222", 12201))
		pToG = GraylogHandler()
		for srv in pToG.graylog_servers:
			self.assertIn(srv, server_list, "Unable to find server in list.")
	
	#----------------------------------------------------------------------
	def testServerConfigHostPortTypeError(self):
		server_list = (("localhost", "12201"), )
		self.assertRaises(TypeError, lambda: GraylogHandler(servers = server_list))
	
	#----------------------------------------------------------------------
	def testServerConfigHostTypeError(self):
		server_list = ((123, 12201), )
		self.assertRaises(TypeError, lambda: GraylogHandler(servers = server_list))	

if __name__ == "__main__":
	unittest.main(verbosity=5)