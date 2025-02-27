# LinTool
This is a linearization tool for minimizing relaxation errors (rank errors) in queues. It computes the rank error per file and linearization method if specified in input arguments. Alternatively, it computes the rank error for multiple files and linearization methods and produces a bar plot.

# Instructions for running

## Ensure correct filepath setup
There is a filepath dependency between semantic-relaxation repository and this one. The filepath for outputting timestamps (in sematic-relaxation > Include > relaxation_linearization_timestamp.c) should be set to the "timestamps" folder in this project.

In the semantic-relaxation repo, we have added functionality to generate timestamp files for some queues (2Dd_optimized, d-cbo, faaaq).

## Python package dependencies
- numpy
- matplotlib.pyplot

## How to run
### Option 1: Run a single file and linearization method
Run the linearizationTool.py script with input arguments ```<filename> <linearization method>```. 

Example (Windows): ```py linearizationTool.py dcbo-n16-d10-w8.csv start```

### Option 2: Run in plot mode
Configure which files, which linearization methods and which measurements should be used in the file linearizationTool.py. 

Run linearizationTool.py without input arguments. Example (Windows): ```py linearizationTool.py```.


# Ideas for algorithm development
some sort of sliding window solution looking at about 10-15 values and then sliding the window about half of the width. aligning the values in the window as good as possible
sorting by some good value

for the good value we can try to find an optimal ration for our naive lineraization value very dum solution :) look for a ratio between the start and end value of each that minimizes the total and mean rank error.
about (end - start) / some value between 0 and 1. linearization point = start + ratio try like 100 different values and return the smallest. 

alternative : linear programming:
objective function minimize total rank error
each enq and deq value limited by the start and end value of the operation. 