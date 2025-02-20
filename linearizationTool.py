# SCRIPT DESCRIPTION
# filename: name of a file to compute. Ignored if version == "plot"
# version: name of a linearization method, or "plot" to plot comparisons between methods
# Parses timestamp file(s) and calls linearization function on the file content, 
# and calls a compute rank error function on the linearization.
# Takes filename and type of linearization function as input.
import csv
import sys
import glob
import os
import numpy as np 
import matplotlib.pyplot as plt
from enum import Enum 
f = None
from linStart import naive_start
from linEnd import naive_end
from computeRankError import compute_rank_error
from linMid import naive_mid
# input file
filename = sys.argv[1]          # TODO: Vore najs om det gick att göra denna optional på något sätt, för plot-körningar
# linearization function
version = sys.argv[2]

class StatType(Enum):       # Not sure this is the correct setup for Enums in Python
    MEAN = 1
    TOTAL = 2
    MAX = 3
    VARIANCE = 4

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

def get_timestamps_from_file(filename):
    timestamps = dict() ## initiate dict for timestamps
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
    return timestamps

# Returns a list of timestamp lists and a list of filenames
# TODO: Maybe remove
def get_timestamps_from_all_files():
    all_timestamps = []
    all_filenames = []
    for file in glob.glob("./timestamps/*.csv", recursive=True):    # This takes a couple of seconds...
        file_name = os.path.relpath(file, "./timestamps/")
        all_timestamps.append(get_timestamps_from_file(file_name))
        all_filenames.append(file_name)
    return (all_timestamps, all_filenames)

# rank_error_type: StatType
# file_selection: list of files which has been used to compile the results
# results: list of lists of computation results (one list of results per lin method)
# lin_method: string to be displayed in plot
def create_plot(rank_error_type, file_selection, all_results, all_lin_methods):

    # Gets the correct measurement and saves it per file instead of per linearization method
    result_per_files = []
    for index, file in enumerate(file_selection):
        result_file = []
        for result_per_lin in all_results:
            (tot_put, tot_get, tot_rank_error, max_rank_error, mean_rank_error, rank_error_variance) = result_per_lin[index]
            match rank_error_type:
                case StatType.MEAN:
                    result_file.append(mean_rank_error)
                case StatType.TOTAL:
                    result_file.append(tot_rank_error)
                case StatType.MAX:
                    result_file.append(max_rank_error)
                case StatType.VARIANCE:
                    result_file.append(rank_error_variance)
        result_per_files.append(result_file)
    
    nr_lin_methods = len(all_lin_methods)
    nr_files = len(file_selection)
    X_axis = np.arange(nr_lin_methods) 
    nr_bars = nr_files * nr_lin_methods
    bar_width = nr_lin_methods / (nr_bars + nr_lin_methods * 2) # TODO: Maybe make the "2" a constant. Higher number => thinner bars

    for index, file_res in enumerate(result_per_files):
        bar_pos = X_axis + (bar_width * 0.5) + ( - (nr_files / 2) * bar_width) + (index * bar_width) # TODO: Test this for more files and more lin methods. Also maybe clean up lol
        plt.bar(bar_pos, file_res, bar_width, label=file_selection[index])
    
    plt.xticks(X_axis, all_lin_methods) 
    plt.xlabel("Linearization methods") 
    plt.ylabel("Rank error") 
    title = "Rank error: " + rank_error_type.name
    plt.title(title) 
    plt.legend() 
    plt.show() 

def print_data(all_filenames, all_results, lin_method):
    print("\nLinearization method: ", lin_method)
    for index, res in enumerate(all_results):
        (tot_put, tot_get, tot_rank_error, max_rank_error, mean_rank_error, rank_error_variance) = res
        print("\nFile name: ", all_filenames[index])
        print("Number of put operations: ", tot_put)
        print("Number of get operations: ", tot_get)
        print("Max rank error: ", max_rank_error)
        print("Total rank error: ", tot_rank_error)
        print("Mean rank error: ", mean_rank_error)
        print("Rank error variance: ", rank_error_variance)

# TODO: Maybe we should have an input argument (perhaps the first arg) to determine which type of relaxation results we want to plot for
match version:
    case "start":
        results = []
        files = [filename]
        (puts,gets) = naive_start(get_timestamps_from_file(filename))
        results.append(compute_rank_error(puts, gets))
        print_data(files, results, "START TIMESTAMPS")
    case "end":
        results = []
        files = [filename]
        (puts,gets) = naive_end(get_timestamps_from_file(filename))
        results.append(compute_rank_error(puts, gets))
        print_data(files, results, "END TIMESTAMPS")
    case "mid":
        (puts, gets) = naive_mid(timestamps)
        print("mean timestamp")
        compute_rank_error(puts, gets)
    case "plot":
        #(all_timestamps, all_filenames) = get_timestamps_from_all_files() # We probably don't wanna get all of them now that I think of it
        
        file_selection = ["faaaq-n16-d10.csv", "dcbo-n16-d10-w16.csv", "2Ddo-n16-d10-w16-l128.csv"]
        all_timestamps = []
        all_lin_methods = []
        for filename in file_selection:
            all_timestamps.append(get_timestamps_from_file(filename))

        results_start = []                                        # list of tuples
        results_end = []

        for ts in all_timestamps:
            (start_puts, start_gets) = naive_start(ts)
            results_start.append(compute_rank_error(start_puts, start_gets))
            (end_puts, end_gets) = naive_end(ts)
            results_end.append(compute_rank_error(start_puts, start_gets))
        
        all_lin_methods.append("Start timestamps")
        all_lin_methods.append("End timestamps")

        print_data(file_selection, results_start, all_lin_methods[0])
        print_data(file_selection, results_end, all_lin_methods[1])

        all_results = []
        all_results.append(results_start)
        all_results.append(results_end)

        # Creates plot which shows MEAN relaxation error for start and end methods
        create_plot(StatType.MEAN, file_selection, all_results, all_lin_methods)

        