# LinTool
Linearization tool for minimizing relaxation errors in queues.

# Instructions for running
There is a filepath dependency between semantic-relaxation repository and this one. The filepath for outputting timestamps (in sematic-relaxation > Include > relaxation_linearization_timestamp.c) should be set to the "timestamps" folder in this project.

## Python package dependencies
- pandas

### Tool structure goal
- parse data from file
-> linearize
-> compute rank error



## algorithm talks
some sort of sliding window solution looking at about 10-15 values and then sliding the window about half of the width. aligning the values in the window as good as possible
sorting by some good value

for the good value we can try to find an optimal ration for our naive lineraization value very dum solution :) look for a ratio between the start and end value of each that minimizes the total and mean rank error.
about (end - start) / some value between 0 and 1. linearization point = start + ratio try like 100 different values and return the smallest. 

alternative : linear programming:
objective function minimize total rank error
each enq and deq value limited by the start and end value of the operation. 