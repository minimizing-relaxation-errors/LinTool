import sys
import math
from timestamp_from_file import get_timestamps_from_file, get_existing_lin

def shorten(timestamp, first_timestamp):
    div = 1000
    return (timestamp - first_timestamp) / div # Milliseconds (given input in nanoseconds)

# Returns interval dict item:(enq_start, enq_end, deq_start, deq_end) and item:(enq, deq)
# with smaller numbers. Returns None for None deq_start/deq_end.
def compress_timestamps(filename):
    timestamps = get_timestamps_from_file(filename)
    lin = get_existing_lin(filename)

    # Find first enqueue timestamps (first of all timestamps)
    first_enq = math.inf
    for ts in timestamps.values():
        e_s = ts.enq_start
        if e_s < first_enq: first_enq = e_s
    
    intervals = {} 
    lin_out = {} 
    for item, ts in timestamps.items():
        e_s = shorten(ts.enq_start, first_enq)
        e_e = shorten(ts.enq_end, first_enq)
        (d_s, d_e) = (ts.deq_start, ts.deq_end)
        if d_s != None:
            d_s = shorten(d_s, first_enq)
            d_e = shorten(d_e, first_enq)
        intervals[item] =  (e_s, e_e, d_s, d_e)
        if lin[item][1] != None:
            lin_out[item] = (shorten(lin[item][0], first_enq), shorten(lin[item][1], first_enq))

    return intervals, lin_out

filename = ""
if len(sys.argv) == 2:
    filename = sys.argv[1]

if __name__=="__main__":

    (intervals, new_lin) = compress_timestamps(filename)

    print("TIMESTAMPS: \n")
    for item, tuple in intervals.items():
        print(item, " : ", tuple)
    print("LIN: \n")
    for item, tuple in new_lin.items():
        print(item, " : ", tuple)
    