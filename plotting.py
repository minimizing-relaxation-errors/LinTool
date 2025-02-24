import numpy as np 
import matplotlib.pyplot as plt
from enum import Enum 


class StatType(Enum):       # Not sure this is the correct setup for Enums in Python
    MEAN = 1
    TOTAL = 2
    MAX = 3
    VARIANCE = 4

# rank_error_type: StatType
# file_selection: list of files which has been used to compile the results
# results: list of lists of computation results (one list of results per lin method)
# lin_method: string to be displayed in plot
def create_plot(rank_error_type: StatType, file_selection, all_results, all_lin_methods):

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


def plot(file_selection, all_timestamps, all_lin_methods):
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