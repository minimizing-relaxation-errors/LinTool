# SCRIPT DESCRIPTION
# Checks if there are any duplicate values in a timestamp file.
# Script takes filename as input.

import csv
import sys
import pandas as pd
f = None

# input file
filename = sys.argv[1]

with open("timestamps/" + filename, newline='') as csvfile:
    filereader = csv.reader(csvfile)

    values = []
    for row in filereader:
        values.append(row[1])

    for val in values:
        occ = values.count(val)
        if (occ > 2):
            print("Value ", val, " occurs ", occ, " times!")
        
            



        