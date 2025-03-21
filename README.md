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

# Code information

## Flow in linearizationTool.py
Responsible calling linearization methods, as well as potential pre and post-processing of data required for the linearization method (see below).

## Two types of linearization methods
Linearization methods are either timestamp or order based. Hence they either
- Expect a timestamp dict which contain value and start and end timestamps for enqueue and dequeue respectively. And output two dicts (puts, gets) which each contain values and decided timestamps for the operation.
- Expect an ordering dict which contains value and a tuple (potential enqueue orders, potential dequeue orders). And output a dict which contain values and tuples (decided enqueue order, decided dequeue order). 

# Code information

## Pikle
un_pickle is in timestamp.py


# Ideas for algorithm development
some sort of sliding window solution looking at about 10-15 values and then sliding the window about half of the width. aligning the values in the window as good as possible (map reduce?)
sorting by some good value (try 25)

for the good value we can try to find an optimal ration for our naive lineraization value very dum solution :) look for a ratio between the start and end value of each that minimizes the total and mean rank error.
about (end - start) / some value between 0 and 1. linearization point = start + ratio try like 100 different values and return the smallest. 

alternative : linear programming:
objective function minimize total rank error
each enq and deq value limited by the start and end value of the operation. 

find possible orderings by looking at overlapping timespans 
choose one with minimal rank error.

Ordering if two operations have the same optimal timestamp?
- test which gives better total ?
- choose arbitrarily because it is alot of computation…?


is our problem NP-c? prove by reduction perhaps
then we know that we can't find an optimal solution in poly time

## pickling orders
to save an ordering from a timestamp file, put it in the list under order in the match case in linearizationTool.py. and run it with _ order as argument

to use the orderings you need to unpickle it

```
with open('saved_dictionary.pkl', 'rb') as f:
    loaded_dict = pickle.load(f)
```



# Tests
- check timestamp file (kind of exists)
- check output linearization points - that enq linearization points are before deq linearization points
    - probably requires comparing ordering to timestamp. consider if this is required
- check that output linearization points/ordering all have unique timestamp/ordering

# Important notes
- vi kan skriva algoritmer som bara funkar för mindre input. “<100000 eller 10000 eller 1000”
- tänk på det som inf när deq inte finns, 
- vill kunna se rank error av varje dequeue.
