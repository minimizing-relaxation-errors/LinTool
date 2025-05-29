'''
SCRIPT DESCRIPTION
Takes two arguments <filename> <linearization method>, outputs the rank errors of an optimized linearization.

This script is responsible for:
- obtaining data from files in respective folders (timestamp or ordering) for linearization methods and necessary utility methods
- calling linearization methods
- (if using ordering) post-processing to timestamps
- calling tests on the outputted linearization (and possibly on the ordering)
- writing the rank error values and test results to a file

'''

# SCRIPT DESCRIPTION
# 
# Parses timestamp and calls linearization function on the file content, 
# and calls a compute rank error function on the linearization.

# If no arguments are set, it will use hard coded values to generate bar plots,
# for multiple files and linearization methods.
import sys
import datetime
from enum import Enum, auto

from lin_methods.lin_start import naive_start
from lin_methods.lin_end import naive_end
from lin_methods.lin_mid import naive_mid
from lin_methods.lin_seventyfive import naive_seven_five
from lin_methods.lin_twentyfive import naive_two_five
from lin_methods.lin_ILP import integer_linear_programming
from lin_methods.lin_window_LP import windowed_linear_programming
from lin_methods.lin_try import exhaustive_ratio, plot_tries
from lin_methods.lin_interchange import interchange
from lin_methods.lin_ordering import ordering_lin

from utils.compute_rank_error import compute_rank_error
from utils.un_pickle import un_pickle
from utils.decided_ordering_to_timestamp import order_to_timestamp
from utils.timestamp_from_file import get_timestamps_from_file, get_existing_lin

from tests.test_timestamp_dict import test_timestamp_dict
from tests.test_order_dict import test_if_order_valid

filename = ""
method_name = "" 
if len(sys.argv) == 3:
    filename = sys.argv[1] 
    method_inp = sys.argv[2]

class Linearization(Enum):
    Start = auto()
    End = auto()
    Mid = auto()
    Twentyfive = auto()
    Seventyfive = auto()
    LP = auto()
    ILP = auto()
    Interchange = auto()
    MultiProbe = auto()
    Order = auto()

# Returns readible string of the results
def get_print_data(filename, results, lin_method: Linearization):
    (tot_put, tot_get, tot_rank_error, max_rank_error, mean_rank_error, rank_error_variance) = results
    out_str = ("\nLinearization method: " + lin_method.name +
           "\nFile name: " + str(filename) + 
           "\nNumber of put operations: " + str(tot_put) + 
           "\nNumber of get operations: " + str(tot_get) + 
           "\nMax rank error: " + str(round(max_rank_error,2)) + 
           "\nTotal rank error: " + str(round(tot_rank_error,2)) + 
           "\nMean rank error: " + str(round(mean_rank_error,2)) + 
           "\nRank error variance: " + str(round(rank_error_variance,2)))
    return out_str

def get_time_diff(start_t, end_t):
    diff = (end_t-start_t)
    out_str = "Time: " + str((diff / datetime.timedelta(microseconds=1))/(60 * 1000000)) + " minutes"
    return out_str

if __name__=="__main__":
    if filename == "" or method_inp == "": sys.exit("Filename and/or method not specified")
    operation_intervals = get_timestamps_from_file(filename) # Called "timestamps" before
    results = None
    (puts,gets) = (None, None)
    method = None
    ordering = None # Optional, if using ordering for lin method
    decided_ordering_dict = None # Optional, if using ordering for lin method
    out_str = "" # Optional
    output_file_name = ""
    start_t = datetime.datetime.now()
    print(start_t)
    match method_inp:
        case "start":
            (puts,gets) = naive_start(operation_intervals)
            method = Linearization.Start
        case "end":
            (puts,gets) = naive_end(operation_intervals)
            method = Linearization.End
        case "mid":
            (puts, gets) = naive_mid(operation_intervals)
            method = Linearization.Mid
        case "twofive":
            (puts, gets) = naive_two_five(operation_intervals)
            method = Linearization.Twentyfive
        case "sevenfive": 
            (puts, gets) = naive_seven_five(operation_intervals)
            method = Linearization.Seventyfive
        case "ilp":
            ordering = un_pickle("orders", filename)
            decided_ordering_dict = integer_linear_programming(ordering)    
            method = Linearization.ILP
            try:
                (puts, gets) = order_to_timestamp(operation_intervals, decided_ordering_dict)    # May throw exception
            except Exception as e:
                sys.exit("Exception raised in order_to_timestamp: ", e) # Not tested
        case "lp":
            (puts, gets) = windowed_linear_programming(operation_intervals, 300, 300)
            method = Linearization.LP
        case "mulpro":
            plot = False
            if not plot:
                (puts, gets) = exhaustive_ratio(operation_intervals, False)
                method = Linearization.MultiProbe
            else:
                res = exhaustive_ratio(get_timestamps_from_file(filename), plot)
                plot_tries(res)
        case "interchange":
            nr_iterations = 30
            nr_swaps_stopping_criteria = 10
            (puts, gets, out_str) = interchange(get_existing_lin(filename), operation_intervals, nr_iterations, nr_swaps_stopping_criteria)
            method = Linearization.Interchange
            output_file_name = str(Linearization.Interchange.name) + "-" + filename + "-iterations-" + str(nr_iterations)
            out_str += ("Max number of iterations: " + str(nr_iterations) + 
                        "\nNumber of swaps stopping critera: " + str(nr_swaps_stopping_criteria))
        case "linord":
            inp = un_pickle("orders", filename)
            file = get_timestamps_from_file(filename)
            ordering_dict = ordering_lin(inp, file)
            method = Linearization.Order
            try:
                puts, gets = order_to_timestamp(file, ordering_dict)
            except Exception as e:
                sys.exit("Exception raised in order_to_timestamp: ", e) # Not tested
    end_t = datetime.datetime.now()
    print(end_t)
    time_diff_str = get_time_diff(start_t, end_t)

    if output_file_name == "":
        output_file_name = str(method.name) + "-" + filename

    results = compute_rank_error(puts, gets)
    print_data_str = get_print_data(filename, results, method)

    # Tests only for the optional, intermediate ordering
    if ordering != None and decided_ordering_dict != None:
        (has_passed_order_tests, order_test_str) = test_if_order_valid(ordering, decided_ordering_dict) # Not tested with dequeue None
        if has_passed_order_tests: print_data_str += "\nPASSED All order tests!"
        else: print_data_str += "\nFAILED Order tests failed!\n" + order_test_str

    # Tests for the final timestamp dict
    (has_passed_tests, test_str) = test_timestamp_dict(puts, gets, operation_intervals)
    # Sanity check - all tests should pass at this stage of development
    if has_passed_tests: print_data_str += "\nPASSED All timestamp tests passed!"
    else: print_data_str += "\nFAILED Timestamp tests failed!\n" + test_str

    f = open("benchmarking_temps/" + output_file_name + ".txt", "w")
    f.write("\n" + out_str + "\n" + print_data_str + "\n" + time_diff_str)
    f.close()

    