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
import xml.etree.ElementTree as ET

RESPONSE_TEXT_TEMPLATE = '''
<xml>
<ToUserName><![CDATA[{ToUserName}}]]></ToUserName>
<FromUserName><![CDATA[gh_6b3b8890948b]]></FromUserName>
<CreateTime>{TIME_STEMP}}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[你好，系统尚在测试中……您刚才说的是：{Content}]]></Content>
</xml>
'''  


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

		dataDict = self.xmlToDict(data)
		print dataDict

		dataDict['TIME_STEMP'] = str(timeHelper.unixTimeStamp())

		text = self.responseXML(dataDict)
		print text
		self.wfile.write(text)

	def xmlToDict(self, xmlText):
		xmlDict = {}
		itemlist = ET.fromstring(xmlText)
		for child in itemlist:
			xmlDict[child.tag] = child.text
		return xmlDict

	def responseXML(self, dataDict):
		text = RESPONSE_TEXT_TEMPLATE 
		for key, value in dataDict.items():
			parameter = '{%s}' % key
			text = text.replace(parameter, value)
		return text
		
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