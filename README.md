# LinTool
This is a linearization tool for minimizing relaxation errors (rank errors) in queues. It computes the rank error per file and linearization method if specified in input arguments. Alternatively, it computes the rank error for multiple files and linearization methods and produces a bar plot.

# Instructions for running

## Ensure correct filepath setup
In the semantic-relaxation repo, we have added functionality to generate timestamp files for some queues (2Dd_optimized, d-cbo, faaaq).

There is a filepath dependency between semantic-relaxation repository and this one. The filepath for outputting timestamp files (defined in sematic-relaxation > Include > relaxation_linearization_timestamp.c) should be set to the "timestamps" folder in this repo.

## Python package dependencies
- numpy
- matplotlib.pyplot
- (and more)

## How to run
### Option 1: Run a single file and linearization method
Run the linearizationTool.py script with input arguments `<filename> <linearization method>`. 

Example (Windows): `py linearizationTool.py dcbo-n16-d10-w8.csv start`

### Option 2: Run in plot mode
Configure which files, which linearization methods and which measurements should be used in the file linearizationTool.py. 

Run linearizationTool.py without input arguments. Example (Windows): `py linearizationTool.py`.

# Code information

## Flow in linearizationTool.py
linearizationTool.py is responsible for calling linearization methods, as well as potential pre and post-processing of data required for the linearization method (see below).
It assumes all files from which data is obtained exist in their respective folders (timestamps or ordering)

## Two types of linearization methods
Linearization methods are either timestamp or order based. Hence they either...

Take as input: a timestamp dict which contain (operation) value as key and a tuple (start timestamp, end timestamp) as value, for enqueue and dequeue respectively. 

And output: two dicts as a tuple (puts, gets) which each contain (operation) values and decided timestamps for the operation.

Or...

Takes as input: an ordering dict which contains value and a tuple (potential enqueue orders, potential dequeue orders). 

And output: a dict which contain values and tuples (decided enqueue order, decided dequeue order). 

For this output, linearizationTool.py needs to call order_to_timestamp in decidedOrderingToTimestamp.py to convert the order dict to two timestamp dict, which can then be inputted into the compute_rank_error function.

## Utility files and functions
(To be written)

# Preparing files
To prepare files, the workflow is as follows: Either generate a .csv file from the semantic-relaxation repo, or use an existing .csv file to create a shorter version, using create_short_file.py in this repo. Then, if using a linearization method that requires an ordering format, use time_ordering.py to create a .pkl file containing the order. Using the function un_pickle, you can extract the order as a dictionary.

## Generate .csv file from semantic-relaxation repo
Requires Linux or using WSL on Windows.

Must use the [semantic-relaxation](https://github.com/minimizing-relaxation-errors/semantic-relaxation) repo which is under the same [Github organization](https://github.com/minimizing-relaxation-errors) as this repo. And when compiling, you must use our flag enable generating timestamps.

Compile with our APPROX flag and VALIDATESIZE=0 per recommendation from supervisor: 

`VALIDATESIZE=0 make faaaq RELAXATION_ANALYSIS=APPROX`

Where "faaaq" is the name of the data structure. We have implemented generating timestamps for faaaq, dcbo-faaaq, 2Dd-queue and 2Dd-queue_optimized.

Run using the binary file of the compiled data structure:

`./bin/faaaq -n 16 -d 1`

-n is the flag for number of cores to use, and -d is the flag for number of milliseconds to run. See the [semantic-relaxation](https://github.com/minimizing-relaxation-errors/semantic-relaxation) repo README for more information on these flags.

## Create shorter .csv file
During development, smaller files have been necessary to test methods on. There is a utility function create_short_file() in create_short_file.py which removes all operations with dequeue value None (to enable sorting), then keeps the "length" first dequeues and their corresponding enqueues.

Run script with inputs \<filename> and \<length>, where filename is an existing .csv file's filename and length is the number of values (and length of generated file). This generates a file that is placed in the timestamp folder, with a name different from but based on the inputted filename.

Example (Windows): `py create_short_file.py faaaq-n15-d10.csv 300`

## Create potential orders (pickling 🥒)
Configure which files are to be pickled by writing the filenames in time_ordering.py (in the list "files"). 

Then run the ordering script. Example Windows: `py time_ordering.py`

This creates a file "filename.pkl" in orders folder.

### Unpickle

There is a function un_pickle that takes a filename and assumes there is a .pkl file with this name. It then extracts the data (potential orders) and outputs it as a dictionary of the form: { operation_value : ([potential enq orders], [potential deq orders]) }. 

The un_pickle function is called from linearizationTool before calling a linearization method that expects orders as input.

# Linearization methods
## Idas very good linearization method
(To be written)

## Linear programming
Scales badly :D
Requires ordering.
(To be written)

# Ideas for algorithm development (TODO)
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

# Ideas for proving things
We know the relaxation error can be at most size of window in 2Dd. I.e. number of items that can be dequeued. 

# Tests (TODO)
- check timestamp file (kind of exists)
- check output linearization points - that enq linearization points are before deq linearization points
    - probably requires comparing ordering to timestamp. consider if this is required
- check that output linearization points/ordering all have unique timestamp/ordering

# Viktiga kommentarer från handledaremöte (TEMP)
- vi kan skriva algoritmer som bara funkar för mindre input. “<100000 eller 10000 eller 1000”
- tänk på det som inf när deq inte finns, 
- vill kunna se rank error av varje dequeue.
