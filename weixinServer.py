# -*- coding: UTF-8 -*-

import posixpath
import urllib
import shutil
import os
from os  import path
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import socket
from SocketServer import ThreadingMixIn
import threading
import sys
import hashlib


class Handler( BaseHTTPRequestHandler ):
	TOKEN = 'this_is_my_token'

	def do_GET(self):
		print threading.currentThread().getName()
		print self.path
		self.getParams = self.requestGet()
		print self.getParams
		print self.isWeixinSignature()
		self.sendResponse()


		return
		
	def requestGet(self):
		paramDict = {}
		pathParts = self.path.split('?', 1)
		if len(pathParts) < 2: return paramDict
		get_str = pathParts[1]
		if not get_str: return paramDict
		parameters = get_str.split('&')
		for param in parameters:
			pair = param.split('=')
			key = pair[0]
			value = pair[1]
			paramDict[key] = value
		return paramDict


	def isWeixinSignature(self):
		signature = self.getParams['signature']
		timestamp = self.getParams['timestamp']
		nonce = self.getParams['nonce']
		echostr = self.getParams['echostr']
		wishSignature = self.localSignature(self.TOKEN, timestamp, nonce)
		print signature, wishSignature
		if signature == wishSignature:
			return True
		return False

		
		
	def sendResponse(self):
		text = self.getParams['echostr']
		self.send_head(text)
		self.wfile.write(text)
		self.wfile.write('\n')
		self.wfile.close()
	
	
	def send_head(self, text):
		self.send_response(200)
		self.send_header("Content-type", 'text/html')
		
		fullLength = len(text)
		print fullLength
		self.send_header("Content-Length", str(fullLength))
		self.send_header("Cache-Control", 'must-revalidate');
		self.end_headers()
		return

		
	def localSignature(self, token, timestamp, nonce):
		items = [token, timestamp, nonce]
		items.sort()
		sha1 = hashlib.sha1()
		map(sha1.update,items)
		hashcode = sha1.hexdigest()
		return hashcode

	

		
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
	
if __name__ == '__main__':
	server_address = ('', 8181) #('localhost', 8181)
	#server = HTTPServer( server_address, Handler)
	server = ThreadedHTTPServer( server_address, Handler)
	print 'Download server is running at http://127.0.0.1:8181/'
	print 'Starting server, use <Ctrl-C> to stop'
	server.serve_forever()