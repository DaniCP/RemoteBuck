'''
Created on 4 de ago. de 2016

@author: daniel.cano
@purpose: To sumarize the results created by validation bench
'''
import sys
reload(sys)
sys.setdefaultencoding('latin-1')

import xlsxwriter
import os
import csv
from time import sleep
path = 'D:/Workspace/Verificaciones/16_08_04_GraderN_x14_util/'

# Create an new Excel file
workbook = xlsxwriter.Workbook(path+'sumary_results.xlsx')
sumary_sheet = workbook.add_worksheet('sumary')
# header
sumary_sheet.write(0, 0, 'sample')
sumary_sheet.write(0, 1, 'barrido1')
sumary_sheet.write(0, 2, 'barrido2')
sumary_sheet.write(0, 3, 'cpm1')
sumary_sheet.write(0, 4, 'cpm2')
sumary_row_num = 1

BARRIDO = 183
B_TOL = 3
CPM1 = 30
CPM2 = 40
CPM_TOL = 0.05
ok_format = workbook.add_format({'fg_color': '#078446'})     # green
fail_format = workbook.add_format({'fg_color': '#ff4949'})  # red

# '''search for .csv and read data'''
for root, dirs, files in os.walk(path):
    for name in files:
        if name.endswith(("R.csv")):
            ifile = open(path+name, 'rb')
            reader = csv.reader(ifile, delimiter=';')
#             add a worksheet.
            worksheet = workbook.add_worksheet(name)
            row_num = 0

            sumary_sheet.write(sumary_row_num, 0, name[:-5])    # sample number
            for row in reader:
                # organize data in sumary tab
                if row[0].upper().find('LOW') != -1 and row[1].upper().find('BARRIDO') != -1:
                    d = float(row[2].replace(',', '.'))
                    if d<BARRIDO-B_TOL or d>BARRIDO+B_TOL:
                        sumary_sheet.write(sumary_row_num, 1, d, fail_format)   # save barrido1 in col1 in red
                    else:
                        sumary_sheet.write(sumary_row_num, 1, d)   # save barrido1 in col1
                elif row[0].upper().find('HIGH') != -1 and row[1].upper().find('BARRIDO') != -1:
                    d = float(row[2].replace(',', '.'))
                    if d<BARRIDO-B_TOL or d>BARRIDO+B_TOL:
                        sumary_sheet.write(sumary_row_num, 2, d, fail_format)   # save barrido2 in col2 in red
                    else:
                        sumary_sheet.write(sumary_row_num, 2, d)   # save barrido2 in col2
                elif row[0].upper().find('LOW') != -1 and row[1].upper().find('CPM') != -1:
                    d = float(row[2].replace(',', '.'))
                    if d<CPM1*(1-CPM_TOL) or d>CPM1*(1+CPM_TOL):
                        sumary_sheet.write(sumary_row_num, 3, d, fail_format)   # save cpm1 in col3 in red
                    else:
                        sumary_sheet.write(sumary_row_num, 3, d)   # save cpm1 in col3
                elif row[0].upper().find('HIGH') != -1 and row[1].upper().find('CPM') != -1:
                    d = float(row[2].replace(',', '.'))
                    if d<CPM2*(1-CPM_TOL) or d>CPM2*(1+CPM_TOL):
                        sumary_sheet.write(sumary_row_num, 4, d, fail_format)   # save cpm2 in col4 in red
                    else:
                        sumary_sheet.write(sumary_row_num, 4, d)   # save cpm2 in col4
                # copy all elements
                col_num = 0
                for element in row:
#                     print name, row_num, col_num, element
                    worksheet.write(row_num, col_num, element)  # copy data
                    col_num += 1
                row_num += 1
            sumary_row_num += 1

workbook.close()
print 'Finished'

