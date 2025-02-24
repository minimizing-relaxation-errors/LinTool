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

f = None
from linStart import naive_start
from linEnd import naive_end
from computeRankError import compute_rank_error
from linMid import naive_mid
from plotting import create_plot, StatType
# input file
filename = sys.argv[1]          # TODO: Vore najs om det gick att göra denna optional på något sätt, för plot-körningar # det går med andra metoder för att ta arbument fråt command line
# linearization function
version = sys.argv[2]



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

def plot(file_selection, all_timestamps, all_lin_methods):
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
        results = []
        files = [filename]
        (puts, gets) = naive_mid(get_timestamps_from_file(filename))
        results.append(compute_rank_error(puts, gets))
        print_data(files, results, "MID TIMESTAMPS")
    case "plot":
        #(all_timestamps, all_filenames) = get_timestamps_from_all_files() # We probably don't wanna get all of them now that I think of it
        file_selection = ["faaaq-n16-d10.csv", "dcbo-n16-d10-w16.csv", "2Ddo-n16-d10-w16-l128.csv"]
        plot(file_selection)
