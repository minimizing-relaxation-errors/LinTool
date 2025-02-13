# SCRIPT DESCRIPTION
# Run script, enter file name of file to be processed (including file ending)
import csv
import os
import sys
import pandas as pd
f = None
# input file
filename = sys.argv[1]
# linearization function
# version = sys.argv[2]

class Timestamp:
    def __init__(self, enq_s, enq_e, deq_s, deq_e):
        self.enq_start = enq_s
        self.enq_end = enq_e
        self.deq_start = deq_s
        self.deq_end = deq_e
    
    def update_deq(self, deq_s, deq_e):
        self.deq_start = deq_s
        self.deq_end = deq_e

timestamps = dict()

with open("timestamps/" + filename, newline='') as csvfile:
    filereader = csv.reader(csvfile)
    for row in filereader:
        if row[2] == 'PUT':
            timestamps.update({row[1]: Timestamp(int(row[3]), int(row[4]), None, None)})
        elif row[2] == 'GET':
            time = timestamps.get(row[1])
            time.update_deq(int(row[3]), int(row[4]))
            timestamps.update({row[1]: time})

#print(timestamps)


#
#table = pd.DataFrame(columns=['val', 'enq_start', 'enq_end', 'deq_start', 'deq_end'], dtype=int)
#temp = pd.DataFrame(columns=['val', 'enq_start', 'enq_end'])
#
#with open("timestamps/" + filename, newline='') as csvfile:
#    filereader = csv.reader(csvfile)
#    for row in filereader:
#        if row[2] == 'PUT':
#            data = {'val': [row[1]], 'enq_start': [row[3]], 'enq_end': [row[4]]}
#            df = pd.DataFrame(data)
#            pd.concat([temp, df], ignore_index=True)
#        elif row[2] == 'GET':
#            print(temp.loc[df['val' == row[1]]])
#        


    
#    words = lines.split(" ")
#    if words[1] == "PUT":