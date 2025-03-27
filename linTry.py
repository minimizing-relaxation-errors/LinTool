import numpy as np
import matplotlib.pyplot as plt
from computeRankError import compute_rank_error

def try_num(inp: dict, num):
    puts = dict()
    gets = dict()
    for i in inp.keys():
        timestamp = inp[i]
        stamp = timestamp.enq_start + (timestamp.enq_end - timestamp.enq_start) * num
        puts.update({i: stamp})
        if timestamp.deq_start != None:
            stamp = timestamp.deq_start + (timestamp.deq_end - timestamp.deq_start) * num
            gets.update({i: stamp})
    return (puts, gets)

def exhaustive_ratio(inp: dict, plot: bool):
    min = 1000000000
    opt_ratio = 0.01
    num = 25
    result = []
    for i in range(num):
        (puts, gets) = try_num(inp, i/num)
        (tot_put, tot_get, tot_rank_error, max_rank_error, mean_rank_error, rank_error_variance) = compute_rank_error(puts, gets)
        result.append((tot_rank_error, max_rank_error, mean_rank_error, rank_error_variance))
        if tot_rank_error < min :
            min = tot_rank_error
            opt_ratio = i/num
    if plot:
        return result
    else:
        return try_num(inp, opt_ratio)

def plot_tries(results):
    x = [x for x in range(1,26)]
    y = [y[2] for y in results]

    fig, ax = plt.subplots()
    ax.plot(x, y, marker = "o", markersize = 5)
    plt.show()