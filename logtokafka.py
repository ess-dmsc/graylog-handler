#!/usr/bin/env python
# -*- coding: utf-8 -*-

from GraylogHandler import GraylogHandler
import logging

#----------------------------------------------------------------------
def main():
	logging.getLogger().setLevel(0)
	logging.getLogger().addHandler(GraylogHandler())
	logging.info("A compressed message.")

if __name__ == "__main__":
	main()