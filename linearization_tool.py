# SCRIPT DESCRIPTION
# Takes two arguments <filename> <linearization method>
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
from lin_methods.lin_order_LP import integer_linear_programming
from lin_methods.lin_window_timestamp_LP import windowed_non_integer_linear_programming
from lin_methods.lin_try import exhaustive_ratio, plot_tries
from lin_methods.lin_ordering import ordering_lin

from utils.compute_rank_error import compute_rank_error
from utils.plotting import create_plot, Measurement
from utils.un_pickle import un_pickle
from utils.decided_ordering_to_timestamp import order_to_timestamp
from utils.timestamp_from_file import get_timestamps_from_file

from tests.test_timestamp_dict import test_timestamp_dict
from tests.validate_timestamp_file import check_duplicate_values_timestamp_file

filename = ""
version = "" 
if len(sys.argv) == 3:
    filename = sys.argv[1] # input file or measurement for plot mode
    version = sys.argv[2] # linearization method or plot mode


class Linearization(Enum):
    Start = auto()
    End = auto()
    Mid = auto()
    Twentyfive = auto()
    Seventyfive = auto()
    LP = auto()
    LPO = auto()
    TryTwentyFive = auto()


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
        print("Max rank error: ", round(max_rank_error,2))
        print("Total rank error: ", round(tot_rank_error,2))
        print("Mean rank error: ", round(mean_rank_error,2))
        print("Rank error variance: ", round(rank_error_variance,2))

def print_time_diff(start_t, end_t):
    diff = (end_t-start_t)
    print("Time:", (diff / datetime.timedelta(microseconds=1))/1000000) # TODO: Might want to do some fancier printouts here later (hours/seconds/milliseconds/microseconds)

def start_time():
    print(datetime.datetime.now())
    start_t = datetime.datetime.now()
    return start_t

def end_time():
    end_t = datetime.datetime.now()
    print(datetime.datetime.now())
    return end_t

if __name__=="__main__":
    results = []
    files = [filename]
    match version:
        # naive solutions start
        case "start":
            start_t = start_time()
            (puts,gets) = naive_start(get_timestamps_from_file(filename))
            end_t = end_time()
            results.append(compute_rank_error(puts, gets))
            print_data(files, results, Linearization.Start)
            print_time_diff(start_t, end_t)
        case "end":
            (puts,gets) = naive_end(get_timestamps_from_file(filename))
            results.append(compute_rank_error(puts, gets))
            print_data(files, results, Linearization.End)
        case "mid":
            (puts, gets) = naive_mid(get_timestamps_from_file(filename))
            results.append(compute_rank_error(puts, gets))
            print_data(files, results, Linearization.Mid)
        case "twofive":
            (puts, gets) = naive_two_five(get_timestamps_from_file(filename))
            results.append(compute_rank_error(puts, gets))
            print_data(files, results, Linearization.Twentyfive)
        case "sevenfive": 
            (puts, gets) = naive_seven_five(get_timestamps_from_file(filename))
            results.append(compute_rank_error(puts, gets))
            print_data(files, results, Linearization.Seventyfive)
        # naive solutions end
        case "lpo": # LP with orders
            timestamps = get_timestamps_from_file(filename)
            start_t = start_time()   
            decided_ordering_dict = integer_linear_programming(un_pickle(filename))    
            end_t = end_time()
            try:
                (puts, gets) = order_to_timestamp(timestamps, decided_ordering_dict)    # May throw exception
                res = test_timestamp_dict(puts, gets, timestamps)
                if res:
                    results.append(compute_rank_error(puts, gets))
                    print_data(files, results, Linearization.LPO)
            except Exception as e:
                print("Something went wrong: ", e)  # Not tested
            print_time_diff(start_t, end_t)
        case "lp":
            original_timestamps = get_timestamps_from_file(filename)
            start_t = start_time()
            (puts, gets) = windowed_non_integer_linear_programming(original_timestamps, 300, 300)
            end_t = end_time()
            res = test_timestamp_dict(puts, gets, original_timestamps)
            if res:
                results.append(compute_rank_error(puts, gets))
                print_data(files, results, Linearization.LP)
            print_time_diff(start_t, end_t)
        case "try25":
            start_t = start_time()
            plot = False
            if not plot:
                (puts, gets) = exhaustive_ratio(get_timestamps_from_file(filename), False)
                results.append(compute_rank_error(puts, gets))
                print_data(files, results, Linearization.TryTwentyFive)
            else: 
                res = exhaustive_ratio(get_timestamps_from_file(filename), plot)
                plot_tries(res)
            end_t = end_time()
            results.append(compute_rank_error(puts, gets))
            print_data(files, results, Linearization.TryTwentyFive)
            print_time_diff(start_t, end_t)
        case "linord":
            inp = un_pickle(filename)
            ordering_lin(inp, filename)
        case _:
            # TODO: could be set in a json file or something
            file_selection = ["faaaq-n16-d10.csv"]
            all_lin_methods = [Linearization.Start, Linearization.Mid, Linearization.End]
            measurement = Measurement.Mean
            all_results = compute_result_plot_mode(file_selection, all_lin_methods)
            
            for i, lm in enumerate(all_lin_methods):
                print_data(file_selection, all_results[i], lm)

            # Creates plot which shows MEAN relaxation error for start and end methods
            create_plot(measurement, file_selection, all_results, all_lin_methods)