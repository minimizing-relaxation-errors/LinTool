# SCRIPT DESCRIPTION
# Run script, enter file name of file to be processed (including file ending)
import csv
import os
import sys
import pandas as pd
f = None
from naiveLin import naive_lin
from computeRankError import compute_rank_error
# input file
filename = sys.argv[1]
# linearization function
version = sys.argv[2]

## Time stamp class, creating object containing 4 timestamps
class Timestamp:
    def __init__(self, enq_s, enq_e, deq_s, deq_e):
        self.enq_start = enq_s
        self.enq_end = enq_e
        self.deq_start = deq_s
        self.deq_end = deq_e
    # we know the enq times before the deq times so we have a function to add them later
    def update_deq(self, deq_s, deq_e):
        self.deq_start = deq_s
        self.deq_end = deq_e

    def update_enq(self, enq_s, enq_e):
        self.enq_end = enq_e
        self.enq_start = enq_s

## initiate dict for timestamps
timestamps = dict()

with open("timestamps/" + filename, newline='') as csvfile:
    filereader = csv.reader(csvfile)
    for row in filereader:
        ## if function is put (enqueue)
        if row[2] == 'PUT':
            if row[1] in timestamps.keys():
                time = timestamps.get(row[1]) ## find existing timestamp object
                time.update_enq(int(row[3]), int(row[4])) ## update timestamp with deq timestamps
                timestamps.update({row[1]: time})
            else: timestamps.update({row[1]: Timestamp(int(row[3]), int(row[4]), None, None)}) ## add value : (timestamp object with enq timestamps, also typecast to ints)
        ## if function is get (dequeue)
        elif row[2] == 'GET':
            if row[1] in timestamps.keys():
                time = timestamps.get(row[1]) ## find existing timestamp object
                time.update_deq(int(row[3]), int(row[4])) ## update timestamp with deq timestamps
                timestamps.update({row[1]: time}) ## update dict with all timestamps
            else: timestamps.update({row[1]: Timestamp(None, None, int(row[3]), int(row[4]))})



match version:
    case "naive":
        (puts, gets) = naive_lin(timestamps)
        compute_rank_error(puts, gets)

        