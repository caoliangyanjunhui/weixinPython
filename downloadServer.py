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
sys.path.append("../lib")
import pathHelper
import fileHexReading


class Handler( BaseHTTPRequestHandler ):

	def do_GET(self):
		print threading.currentThread().getName()
		if self.isPartialDownloadRequest():
			self.partialTransfer()
		else:
			self.fullTransfer()
		return
		
	def isPartialDownloadRequest(self):
		rangeStr = self.headers.get("RANGE")
		if not rangeStr:
			return False
		ifRangeStr = self.headers.get("IF-RANGE")
		filePath = self.localFilePath( self.fileNameFromHTTPPath (self.path) )
		zipDateTimeTag = fileHexReading.zipFileDateTimeTag( filePath )
		print ifRangeStr.upper() + ' == ' + zipDateTimeTag.upper()
		return ifRangeStr.upper() == zipDateTimeTag.upper()
        
	def requestFileOffset(self):
		#   Range: bytes=9855420-
		start = self.headers.get("Range")
		print start
		try:
			pos = int(start[6:-1])
		except ValueError:
			self.send_error(400, "bad range specified.")
			return None
		return pos
        
        
	def partialTransfer(self):
		# Only support offset to end transfer
		f = self.fileForDownload( self.fileNameFromHTTPPath (self.path) )
		if f:
			pos = self.requestFileOffset()
			self.sendPartialDownlaodHead(pos, f)
			f.seek(pos)
			self.transferFile(f)
		else:
			self.send_error(404, "File not found")
			print '404 File not found: ' + self.path
		return
		
	def sendPartialDownlaodHead(self, pos, f):
		self.send_response(206)
		self.send_header("Content-type", 'application/octet-stream')
		self.send_header("Connection", "keep-alive")
		fs = os.fstat(f.fileno())
		fullLength = fs.st_size
		transferLength = fullLength - pos
		print transferLength
		self.send_header("Content-Length", str(transferLength))
		self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
		contentRange = "bytes %s-%s/%s" % (str(pos), fullLength-1, fullLength) #Content-Range: bytes 64312833-64657026/64657027
		print transferLength
		print contentRange
		self.send_header("Content-Range", contentRange)
		self.send_header("Cache-Control", 'must-revalidate');
		self.end_headers()
		return
        
        
	def fullTransfer(self):
		f = self.fileForDownload( self.fileNameFromHTTPPath (self.path) )
		if f:
			self.send_head(f)
			self.transferFile(f)
		else:
			self.send_error(404, "File not found")
			print '404 File not found: ' + self.path
		return
	
	
	def send_head(self, f):
		self.send_response(200)
		self.send_header("Content-type", 'application/octet-stream')
		fs = os.fstat(f.fileno())
		fullLength = fs.st_size
		print fullLength
		self.send_header("Content-Length", str(fullLength))
		self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
		self.send_header("Cache-Control", 'must-revalidate');
		self.end_headers()
		return

	def localFilePath(self, fileName):
		downloadRootPath = pathHelper.downloadRootPath()
		if fileName.find('.zip') > 0:
			subFolderName = 'db'
		elif fileName.find('.ipa') > 0:
			subFolderName = 'ipa'
		elif fileName.find('.plist') > 0:
			subFolderName = 'ipa'
		elif fileName.find('.html') > 0:
			subFolderName = 'ipa'
		else:
			subFolderName = 'images'
		return os.path.join( downloadRootPath, subFolderName, fileName )
		
	def fileForDownload(self, fileName):
		filePath = self.localFilePath( fileName )
		print filePath
		f = None
		try:
			f = open(filePath, 'rb')
		except IOError:
			return None		
		return f
		
		
	def fileNameFromHTTPPath(self, path):        
		# abandon query parameters
		path = path.split('?',1)[0]
		path = path.split('#',1)[0]
		path = posixpath.normpath(urllib.unquote(path))
		words = path.split('/')
		words = filter(None, words)
		if len(words) > 0:
			return words[-1]
		return None
		
		
	def copyfile(self, source, outputfile):
		"""Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.
		"""
		shutil.copyfileobj(source, outputfile)
		
	def transferFile(self, f):
		try:
			self.copyfile(f, self.wfile)
			self.log_message('"%s" %s', self.requestline, "req finished.")
		except socket.error:
			self.log_message('"%s" %s', self.requestline, "req terminated.")
		finally:
			f.close()
		return None
		
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    
if __name__ == '__main__':
	server_address = ('', 8181) #('localhost', 8181)
	#server = HTTPServer( server_address, Handler)
	server = ThreadedHTTPServer( server_address, Handler)
	print 'Download server is running at http://127.0.0.1:8181/'
	print 'Starting server, use <Ctrl-C> to stop'
	server.serve_forever()