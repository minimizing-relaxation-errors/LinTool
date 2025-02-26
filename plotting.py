import numpy as np 
import matplotlib.pyplot as plt
from enum import Enum, auto 


class Measurement(Enum): 
    Mean = auto()
    Total = auto()
    Max = auto()
    Variance = auto()

# rank_error_type: Measurement
# file_selection: list of files which has been used to compile the results
# all_results: list of lists of computation results (one list of results per lin method)
# lin_method: string to be displayed in plot
def create_plot(rank_error_type: Measurement, file_selection, all_results, all_lin_methods):

    # Gets the correct measurement and saves it per file instead of per linearization method
    result_per_files = []
    for index, file in enumerate(file_selection):
        result_file = []
        for result_per_lin in all_results:
            (tot_put, tot_get, tot_rank_error, max_rank_error, mean_rank_error, rank_error_variance) = result_per_lin[index]
            match rank_error_type:
                case Measurement.Mean:
                    result_file.append(mean_rank_error)
                case Measurement.Total:
                    result_file.append(tot_rank_error)
                case Measurement.Max:
                    result_file.append(max_rank_error)
                case Measurement.Variance:
                    result_file.append(rank_error_variance)
        result_per_files.append(result_file)
    
    nr_lin_methods = len(all_lin_methods)
    nr_files = len(file_selection)
    X_axis = np.arange(nr_lin_methods) 
    nr_bars = nr_files * nr_lin_methods
    bar_width = nr_lin_methods / (nr_bars + nr_lin_methods )
    for index, file_res in enumerate(result_per_files):
        bar_pos = X_axis + (bar_width * 0.5) + ( - (nr_files / 2) * bar_width) + (index * bar_width)
        plt.bar(bar_pos, file_res, bar_width, label=file_selection[index])
    
    plt.xticks(X_axis, [x.name for x in all_lin_methods])
    plt.xlabel("Linearization methods") 
    plt.ylabel("Rank error") 
    title = "Rank error: " + rank_error_type.name
    plt.title(title) 
    plt.legend() 
    plt.show() 