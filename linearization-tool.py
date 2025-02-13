# SCRIPT DESCRIPTION
# Run script, enter file name of file to be processed (including file ending)

import os
f = None

# input
filename = input()

f = open("timestamps/" + filename, "r")

for line in f:
    print(line)
    
#    words = lines.split(" ")
#    if words[1] == "PUT":