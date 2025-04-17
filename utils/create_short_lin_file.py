import csv
import sys
import os

parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Cursed
sys.path.append(parent_path)
from linearization_tool import get_existing_lin
sys.path.remove(parent_path)

# TODO: Clarify that a "10000" file actually contains 10000 dequeues AND 10000 enqueus, i.e. 20000 ops

# NOTE: this script and the create_short_timestamp_file.py script does not result in the same values being stored, 
#       since they sort on different values (this one on "linearization point"/only timestamp value from its file, 
#       the other on start value)

# Takes from command line: <file name> <desired length of new file>
# (Removes dequeue None values)
# Creates another .csv file with 'length' number of operations (with earliest dequeue start values)
# Assumes that a linearization file exists in folder current_linearization_results with name 'filename'
def create_short_lin_file(filename, length_str):
    length = int(length_str)
    timestamps = get_existing_lin(filename) # dictionary of structure item:[enq_timestamp, deq_timestamp]

    timestamps_no_none = {}
    # Remove none to enable easy sorting
    for (k,v) in timestamps.items():
        if(v[1] != None):
            timestamps_no_none[k] = v

    # Sort on deq_start (ascending)
    timestamps_sorted_on_deq = dict(sorted(timestamps_no_none.items(), key=lambda x: x[1][1]))

    # Save "length" first items from sorted dict
    timestamps_small = {}
    for i, (k,v) in enumerate(timestamps_sorted_on_deq.items()):
        if i >= length: break
        timestamps_small[k] = v
    
    # Prints used for confirming results
    print("timestamps dict length: ", len(timestamps_small))
    nr_enqs = 0
    nr_deqs = 0
    for ts in timestamps_small.values():
        if(ts[0] is not None): nr_enqs += 1
        if(ts[1] is not None): nr_deqs += 1
    print("Nr enqs: ", nr_enqs)
    print("Nr deqs: ", nr_deqs)

    # Extract data to use for producing csv
    iterable_for_csv = []
    for (k,v) in timestamps_small.items(): # both enq and deq exists
        iterable_for_csv.append([0, k, "PUT", v[0]])
        iterable_for_csv.append([0, k, "GET", v[1]])

    # Create csv
    new_filename = "current_linearization_results/" + "short-" + length_str + "-" + filename
    with open(new_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(iterable_for_csv)

    return new_filename

if __name__=="__main__":
    filename = sys.argv[1] # input file or measurement for plot mode
    length_str = sys.argv[2] # linearization method or plot mode
    create_short_lin_file(filename, length_str)
