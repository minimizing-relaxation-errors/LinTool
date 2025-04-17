import datetime
from timestamp_from_file import get_timestamps_from_file, get_existing_lin
import pickle
import sys
import os

# Add the parent folder to sys.path
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from lin_methods.lin_interchange import set_deq_none_last


# Saves which items have been enqueued before and which have been dequeued after
# Assumes no dequeue is None
# Return data is dictionary of item:([list of items enqueued before], [list of items dequeued before])
# TODO: FIX NEW STRUCTURE 10:24
def set_order_data(lin):
    order_data = {}
    order_data = dict()
    for (item1, (enq1, deq1)) in lin.items():
        e_bef = []
        d_bef = []
        for (item2, (enq2, deq2)) in lin.items():
            if enq2 < enq1: e_bef.append(item2)
            if deq2 != None:                                            # If deq2 is None, then deq1 happens before and nothing gets stored
                if deq1 == None or deq2 < deq1: d_bef.append(item2)     # If deq1 is None, then deq2 definitely happens before
        order_data[item1] = (e_bef, d_bef)
    print("ORDER DATA: ", order_data)
    return order_data

def time_positioning_pickle(filename):
    print(datetime.datetime.now())
    ordername = "positions/" + filename + ".pkl"
    print("Initiated: Setting Dequeue None last")
    lin_new = set_deq_none_last(get_timestamps_from_file(filename), get_existing_lin(filename))
    print("Finished: Setting Dequeue None last")

    print("Initiated: Setting order data")
    data = set_order_data(lin_new)
    print("Finished: Setting order data")
    with open(ordername, 'wb') as f:
        pickle.dump(data, f)
    print(datetime.datetime.now())

if __name__== "__main__":
    files = ["dcbo-n16-d1-w16.csv"]
    for filename in files:
        time_positioning_pickle(filename)