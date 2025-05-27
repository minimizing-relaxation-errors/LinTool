import matplotlib.pyplot as plt
import numpy as np
import sys
from get_readible_timestamps import compress_timestamps

def plot_intervals(filename):
    (intervals, lin) = compress_timestamps(filename)
        
    # Initialise the subplot function using number of rows and columns
    fig, axis = plt.subplots(1, 2)

    fig.set_figwidth(10)
    fig.set_figheight(3)

    #axis.figure(figsize=(15,3))
    sorted_item_list = [str(i) for i in sorted([int(x) for x in intervals.keys()])] # TODO: This is not great
    
    nr_items = len(sorted_item_list)
    print("Nr items: ", nr_items)
    print(sorted_item_list)
    line = 0.3
    i = 0
    for item in sorted_item_list:
        start = intervals[item][0]
        end = intervals[item][1]
        lin_point = lin[item][0]
        axis[0].hlines(i, start, end)
        axis[0].text(x=lin_point-0.4, y=i-line-0.35,s=str(lin_point), size='xx-small')
        axis[0].vlines(lin_point, i-line, i+line, colors='r',linewidth=1.0)
        i += 1
    axis[0].set_title("Enqueue intervals")
    axis[0].set_xlabel("Time (ms)", size='small')
    axis[0].set_ylabel("Item identifier", size='small')
    axis[0].set_yticks(np.arange(nr_items), sorted_item_list, size='xx-small')

    i = 0
    for item in sorted_item_list:
        start = intervals[item][2]
        end = intervals[item][3]
        lin_point = lin[item][1]
        axis[1].hlines(i,start,end)
        axis[1].text(x=lin_point-0.03, y=i-line-0.35,s=str(lin_point), size='xx-small')
        axis[1].vlines(lin_point, i-line, i+line, colors='r',linewidth=1.0)
        i += 1
    axis[1].set_title("Dequeue intervals")
    axis[1].set_xlabel("Time (ms)", size='small')
    axis[1].set_ylabel("Item identifier", size='small')
    axis[1].set_yticks(np.arange(nr_items), sorted_item_list, size='xx-small')

    plt.tight_layout()
    plt.show()


filename = ""
if len(sys.argv) == 2:
    filename = sys.argv[1]

if __name__=="__main__":
    plot_intervals(filename)