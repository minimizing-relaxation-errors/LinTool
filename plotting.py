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

    fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True) # constrained_layout ensures everything (legend) fits within the window
    fig.set_constrained_layout_pads(w_pad=0.2, h_pad=0.2, hspace=0.2, wspace=0.2)
    
    # Gets the correct measurement and saves it per linearization method
    result_to_use = []
    for result_per_lin in all_results:
        result_file = []
        for index, file in enumerate(file_selection):
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
        result_to_use.append(result_file)
    
    nr_lin_methods = len(all_lin_methods)
    nr_files = len(file_selection)
    X_axis = np.arange(nr_files) 
    nr_bars = nr_files * nr_lin_methods
    bar_width = nr_files / (nr_bars + nr_files)
    for i, file_res in enumerate(result_to_use):
        # Sets positions for bars, trying to evenly distribute them with the x-tick in the middle of a bar cluster
        bar_pos_x = X_axis + (bar_width * 0.5) + ( - (nr_lin_methods / 2) * bar_width) + (i * bar_width)  
        # Adds all bars for every file (automatically handles bar_pos_x and file_res which are both lists)  
        ax.bar(bar_pos_x, file_res, bar_width, label=all_lin_methods[i].name)       
        for j, res in enumerate(file_res):                                          # For every result for a file
            ax.text(bar_pos_x[j], res, round(res, 6), ha='center', size='xx-small') # Add bar text: result rounded to 6 decimals
    
    ax.set_xticks(X_axis)
    ax.set_xticklabels(file_selection)   # Set x labels as file names
    ax.set_xlabel("Files") 
    ax.set_ylabel("Rank error") 
    title = "Rank error: " + rank_error_type.name
    ax.set_title(title) 
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left') # Position legend to the right of plot
    plt.show() 