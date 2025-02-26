# SCRIPT DESCRIPTION
# Takes two arguments <filename> <linearization method>
# Parses timestamp and calls linearization function on the file content, 
# and calls a compute rank error function on the linearization.

# If no arguments are set, it will use hard coded values to generate bar plots,
# for multiple files and linearization methods.
import csv
import sys
from enum import Enum, auto
from linStart import naive_start
from linEnd import naive_end
from computeRankError import compute_rank_error
from linMid import naive_mid
from linSevFiv import naive_seven_five
from lintwofiv import naive_two_five
from plotting import create_plot, Measurement

arg1 = ""
arg2 = "" 
if len(sys.argv) == 3:
    arg1 = sys.argv[1] # input file or measurement for plot mode
    arg2 = sys.argv[2] # linearization method or plot mode



class Linearization(Enum):
    Start = auto()
    End = auto()
    Mid = auto()
    Twentyfive = auto()
    Seventyfive = auto()

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

# Outputs a list of lists
# Each sublist holds the results computed from a certain linearization method, for the entire file selection
def compute_result_plot_mode(file_selection, all_lin_methods):
    all_timestamps = []
    for filename in file_selection:
        all_timestamps.append(get_timestamps_from_file(filename))

    all_results = []
    # For each linearization method, 
    for lm in all_lin_methods:
        # compute rank error for each file
        temp_result = []
        for ts in all_timestamps:
            match lm:
                case Linearization.Start:
                    (start_puts, start_gets) = naive_start(ts)
                    temp_result.append(compute_rank_error(start_puts, start_gets)) 
                case Linearization.End:
                    (end_puts, end_gets) = naive_end(ts)
                    temp_result.append(compute_rank_error(end_puts, end_gets))
                case Linearization.Mid:
                    (mid_puts, mid_gets) = naive_mid(ts)
                    temp_result.append(compute_rank_error(mid_puts, mid_gets))
                case Linearization.Twentyfive:
                    (two_five_puts, two_five_gets) = naive_two_five(ts)
                    temp_result.append(compute_rank_error(two_five_puts, two_five_gets))
                case Linearization.Seventyfive:
                    (seven_five_puts, sevel_five_gets) = naive_seven_five(ts)
                    temp_result.append(compute_rank_error(seven_five_puts, sevel_five_gets))
        all_results.append(temp_result)
    return all_results

# Prints rank error information for each file, for a certain linearization method
def print_data(all_filenames, all_results, lin_method: Linearization):
    print("\nLinearization method: ", lin_method.name)
    for index, res in enumerate(all_results):
        (tot_put, tot_get, tot_rank_error, max_rank_error, mean_rank_error, rank_error_variance) = res
        print("\nFile name: ", all_filenames[index])
        print("Number of put operations: ", tot_put)
        print("Number of get operations: ", tot_get)
        print("Max rank error: ", max_rank_error)
        print("Total rank error: ", tot_rank_error)
        print("Mean rank error: ", mean_rank_error)
        print("Rank error variance: ", rank_error_variance)


results = []
files = [arg1]
match arg2:
    case "start":
        (puts,gets) = naive_start(get_timestamps_from_file(arg1))
        results.append(compute_rank_error(puts, gets))
        print_data(files, results, Linearization.Start)
    case "end":
        (puts,gets) = naive_end(get_timestamps_from_file(arg1))
        results.append(compute_rank_error(puts, gets))
        print_data(files, results, Linearization.End)
    case "mid":
        (puts, gets) = naive_mid(get_timestamps_from_file(arg1))
        results.append(compute_rank_error(puts, gets))

        print_data(files, results, Linearization.Mid)
    case "twofive":
        (puts, gets) = naive_two_five(get_timestamps_from_file(arg1))
        results.append(compute_rank_error(puts, gets))
        print_data(files, results, Linearization.Twentyfive)
    case "sevenfive": 
        (puts, gets) = naive_seven_five(get_timestamps_from_file(arg1))
        results.append(compute_rank_error(puts, gets))
        print_data(files, results, Linearization.Seventyfive)
    case _:
        # TODO: could be set in a json file or something
        file_selection = ["faaaq-n16-d10.csv", "dcbo-n16-d10-w16.csv", "2Ddo-n16-d10-w16-l128.csv"]
        all_lin_methods = [Linearization.Start, Linearization.Mid, Linearization.End]
        measurement = Measurement.Mean

        all_results = compute_result_plot_mode(file_selection, all_lin_methods)
        
        for i, lm in enumerate(all_lin_methods):
            print_data(file_selection, all_results[i], lm)

        # Creates plot which shows MEAN relaxation error for start and end methods
        create_plot(measurement, file_selection, all_results, all_lin_methods)

