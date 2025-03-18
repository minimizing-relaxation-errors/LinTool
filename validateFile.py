# SCRIPT DESCRIPTION
# Checks if there are any duplicate values in a timestamp file.
# Script takes filename as input.

import csv
import sys
from linearizationTool import get_timestamps_from_file
f = None

# input file
filename = sys.argv[1]

with open("timestamps/" + filename, newline='') as csvfile:
    filereader = csv.reader(csvfile)
    timestamps = get_timestamps_from_file(filename)

    enq_fails = 0
    deq_fails = 0
    deq_end_enq_start_fail = 0
    for i in timestamps:
        timestamp = timestamps[i]
        # "Asserts" enqueue start is before enqueue end
        if timestamp.enq_start > timestamp.enq_end:
            enq_fails += 1
        # "Asserts" that dequeue start is before dequeue end
        if timestamp.deq_start is not None:
            if timestamp.deq_start > timestamp.deq_end:
                deq_fails += 1
        # "Asserts" that dequeue end is after enqueue start
        if timestamp.deq_end is not None:
            if timestamp.deq_end < timestamp.enq_start:
                deq_end_enq_start_fails += 1

    keys = []
    for row in filereader:
        key = row[1]
        keys.append(key)
    unique_keys = set(keys)
    key_occ = {}
    for key in unique_keys:
        # Checks if our values (keys in timestamp file) are unique
        occ = keys.count(key)
        key_occ[key] = occ
    
    for key, value in key_occ.items():
        if(value > 2):
            print("Key: ", key, " occurs ", value, " times across both enq and deq operations")

    print("Number of ENQ ends before starts: ", enq_fails)
    print("Number of DEQ ends before starts: ", deq_fails)
    
    print("Finished checking file: ", filename)
