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