# LinTool
This is a tool for finding a linearization of a relaxed FIFO-queue execution, such that the mean rank error per dequeue operation is minimal.
The linearization is created from a history of operation intervals (start and end timestamps of both enqueue and dequeue operations) for each of which it determines a good linearization point.
This history must be provided and the workflow below describes how.

The user specifies which (history) file and which linearization method should be used, and the tool uses the method to produce a linearization and outputs the result (rank error) to file.

# Preparations before running
This section describes how to set up the project and all necessary files before running the tool.
Please note that this repository (_LinTool_) is grouped within a GitHub organization called _minimizing-relaxation-errors_.
Another repository (_semantic-relaxation_) is also part of the organization.
It is based on the code from the DCS Chalmers repository [semantic-relaxation-dcbo](https://github.com/dcs-chalmers/semantic-relaxation-dcbo).

## Ensure correct filepath setup
In the _semantic-relaxation_ repository, we have added functionality to save start and end timestamps for enqueue and dequeue operations, for some queues (2Dd_optimized, d-cbo, faaaq).
The timestamps are saved in CSV files which we mostly refer to as "timestamp files".
Additionally, we print the linearization point timestamps defined by the authors of [semantic-relaxation-dcbo](https://github.com/dcs-chalmers/semantic-relaxation-dcbo) to a separate CSV file, and the results of that linearization to a text file.

Therefore, there are filepath dependencies between the _semantic-relaxation_ repository and this repository. 
The concerned filepaths are all defined in _sematic-relaxation > Include > relaxation_linearization_timestamp.c_. 
The filepath for printing start and end timestamps should be set to the "timestamps" folder in this repo.
The filepath for printing linearization point timestamps and the results of that linearization should be set to the "current_linearization_results" folder in this repo. 

## Python dependencies
### Libraries
- Mathplotlib (pyplot)
- numpy
- cvxpy

### Modules
- Enum
- csv
- sys
- os
- pickle
- datetime
- math

### Relative paths
Python paths are relative to from which directory you run the script.
Scripts must be run from base directory, otherwise there may be issues with dependencies between files and folder or file paths.

## Preparing files
If you wish to run the tool on other files than the ones already provided here, then you will need to create them.

To prepare files, the workflow is as follows: 
Either generate a .csv file from the semantic-relaxation repository, or use an existing .csv file to create a shorter version, using functionality from `create_short_file.py` in this repository. 
Then, if using a linearization method that requires an ordering format, use `time_ordering.py` to create a .pkl file containing the order.

### Generate .csv file from semantic-relaxation repo
Requires Linux or using WSL on Windows.

Must use the [semantic-relaxation](https://github.com/minimizing-relaxation-errors/semantic-relaxation) repository which is under the same [Github organization](https://github.com/minimizing-relaxation-errors) as this repository. 
When compiling, you must use our flag `APPROX` to enable generating files:

`make faaaq RELAXATION_ANALYSIS=APPROX`

where "faaaq" is the name of the data structure. We have implemented generating timestamps for faaaq, dcbo-faaaq, 2Dd-queue and 2Dd-queue_optimized.

Run using the binary file of the compiled data structure:

`./bin/faaaq -n 16 -d 1`

-n is the flag for number of cores to use, and -d is the flag for number of milliseconds to run. See the [semantic-relaxation](https://github.com/minimizing-relaxation-errors/semantic-relaxation) README for more information on more flags.

### Create shorter .csv file
During development, smaller files have been necessary to test methods on. 
There is a utility functionality in `create_short_timestamp_file.py` which takes a `filename` and a variable `length` which specifies the number of items operated on in the new history.
There must exist a file `filename` with more than `length` number of items operated on in the history. 
The script then generates a file which includes the `length` first dequeue operations (of the existing file) and their items' corresponding enqueue operations.
Non-existing dequeues are ignored.
The generated file is placed in the timestamp folder, with a name different from but based on the inputted filename.

Example (Windows): `py create_short_timestamp_file.py faaaq-n15-d10.csv 300`

There is a similar script for creating shorter linearization files.
It requires that the corresponding long linearization file exists, as well as the corresponding short timestamp file exist (it iterates over the short timestamp file, to ensure that the corresponding items are included in the short linearization file).

Example (Windows): `py create_short_lin_file.py faaaq-n15-d10.csv 300`

### Create potential ordering (pickling 🥒)
A potential ordering for an item consists of all possible "positions" of its enqueue and dequeue operations in the total ordering of enqueues and dequeues (respectively).
The script for producing orderings utilizes the pickle python module to  store the data.

Define one or more timestamp files to create orderings from by adding the filenames to the list "files" in time_ordering.py.
Then run the ordering script. Example Windows: `py time_ordering.py`.
This creates one or more files "filename.pkl" in orders folder.

#### Unpickle

The function `unpickle(filename)` in `unpickle.py` returns the data from an existing file filename.pkl as a dictionary of the form { operation_value : ([potential enq orders], [potential deq orders]) }. 

The un_pickle function is called from linearization_tool before calling a linearization method that expects orders as input.

# How to run
Run the tool by calling the main file (`linearization_tool.py`) with input arguments `<filename> <linearization method>`. 

Example (Windows): `py linearization_tool.py dcbo-n16-d10-w8.csv start`

Note that linearization methods assume certain data files exist, according to this table:

| File type             | Method    |
| --------              | -------   |
| Timestamp file        | End<br>Mid<br>Start<br>SeventyFive<br>TwentyFive<br>MultiProbe<br>LP<br>Interchange    |
| Linearization file    | Interchange     |
| Ordering file         | ILP<br>(the final ordering method)    |


