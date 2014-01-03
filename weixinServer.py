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
import timeHelper
import cgi


class Handler( BaseHTTPRequestHandler ):
	TOKEN = 'thisismytoken'

	def do_GET(self):
		print threading.currentThread().getName()
		print self.path
		self.getParams = self.requestGet()
		print self.getParams
		text = 'empty'
		if self.getParams:
			print self.isWeixinSignature()
			text = self.getParams['echostr']
		self.sendResponse(text)
		return

	def do_POST(self):
		form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
					 'CONTENT_TYPE':self.headers['Content-Type'],
					 })
		if form.file:      
			data = form.file.read()   
			print data          
		else:                          
			print "data is None"  
		
		self.send_response(200)
		self.end_headers()
		'''
		self.wfile.write('Client: %s\n' % str(self.client_address))
		self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
		self.wfile.write('Path: %s\n' % self.path)
		self.wfile.write('Form data:\n')
		'''
		text = '''
<xml>
<ToUserName><![CDATA[o456EjonCiPoKk69egF8UNus5HkY]]></ToUserName>
<FromUserName><![CDATA[gh_6b3b8890948b]]></FromUserName>
<CreateTime>[timestamp]</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[你好，系统尚在测试中……]]></Content>
</xml>
'''  
		self.wfile.write(text)
		
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

		
		
	def sendResponse(self, text):
		self.send_head(text)
		self.wfile.write(text)
		self.wfile.close()
	
	
	def send_head(self, text):
		self.send_response(200)
		self.send_header("Content-type", 'text/html')
		fullLength = len(text)
		print fullLength, text
		self.send_header("Content-Length", str(fullLength))
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
	serverPort = 80
	server_address = ('', serverPort) #('localhost', 8181)
	#server = HTTPServer( server_address, Handler)
	server = ThreadedHTTPServer( server_address, Handler)
	print 'Download server is running at http://127.0.0.1:' + str(serverPort)
	print 'Starting server, use <Ctrl-C> to stop'
	server.serve_forever()