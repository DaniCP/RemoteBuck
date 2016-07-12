'''
Created on 2 de jun. de 2016

@author: daniel.cano
@summary: Verification bench takes 20 samples per second and the encoder returns
    same position during a determined time. This script search for increments in
    position column and calculates the speed based on the time transcurred from
    the last position updated.
'''
import csv
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", type=str, default='./',
                    help="paht to the csv file")
parser.add_argument("-f", "--filename", type=str, default='.csv',
                    help="csv file name")
args = parser.parse_args()

# path = args.path
# filemane = args.filename
path = 'D:/Workspace/Verificaciones/valtra_angulos/'
filename = 'valtra2D.csv'

ifile = open(path+filename, 'rb')
reader = csv.reader(ifile, delimiter=';')

''' variable definition '''
rownum = 0
last_change_row_num = 0
old_pos = 0
new_pos = 0
old_speed = 0
changes_counter = 0
speed_list = []
time_list = []
pos_list = []
accel_list = []
i=0
'''csv parse'''
for row in reader:
    # Save header row.
    if rownum == 0:
        header = row
    else:
        if i == 10:
            i = 0
            new_pos = float(row[5].replace(',', '.'))  # read encoder pos, column 5
            pos_list.append(new_pos)  # get position
            if int(new_pos) == 50:
                plt.axvline(x=rownum*0.00005, ymin=0, ymax=360, linewidth=1)
            speed = (new_pos-old_pos) / ((rownum-last_change_row_num)*0.00005)  # deg/s
            speed_rpm = speed*60/360  # rpm
    #             print "time:", rownum*0.00005, "speed: ", speed
            speed_list.append(speed)
    
            acc = (speed-old_speed) / ((rownum-last_change_row_num)*0.00005)  # deg/s2
            accel_list.append(acc)
    
            time_list.append(rownum*0.00005)
            changes_counter += 1
            last_change_row_num = rownum
            old_pos = new_pos
            old_speed = speed
        else:
            i += 1

    rownum += 1


'''moving avg'''
num_elem_avg = 100
speed_averaged = np.convolve(speed_list, np.ones((num_elem_avg,))/num_elem_avg, mode='valid')
time_avg = np.convolve(time_list, np.ones((num_elem_avg,))/num_elem_avg, mode='valid')
pos_avg = np.convolve(pos_list, np.ones((num_elem_avg,))/num_elem_avg, mode='valid')
'print average speed'
print args.filename, " speed: ", abs(np.mean(speed_averaged))
print "speed in 30s: ", new_pos*60/((rownum)*0.00005*360)

'''ploting'''
fig = plt.figure(1)
# plt.subplot(211)
plt.plot(time_avg, pos_avg)
# plt.subplot(212)
plt.plot(time_avg, speed_averaged)
plt.axhline(y=0, xmin=0, xmax=22, linewidth=1)
fig.suptitle(args.filename[:-5], fontsize=12, fontweight='bold')
# plt.plot(time_avg, speed_avg3_list)
# plt.subplot(3,1,3)
# plt.plot(np.convolve(accel_list, np.ones((200,))/200, mode='valid'))
# # plt.plot(accel_list)

if not os.path.exists(args.path +'images/'):
    os.makedirs(args.path +'images/')
plt.savefig(args.path +'images/'+ args.filename[:-5] +'.png')
plt.show()

# print "number of rows: ", rownum, " changes_counter: ", changes_counter
ifile.close()
