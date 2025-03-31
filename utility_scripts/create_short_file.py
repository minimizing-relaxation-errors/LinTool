import csv
import sys
from linearization_tool import get_timestamps_from_file

# Takes from command line: <file name> <desired length of new file>
# (Removes dequeue None values)
# Creates another .csv file with 'length' number of operations (with earliest dequeue start values)

def create_short_file(filename, length_str):
    length = int(length_str)
    timestamps = get_timestamps_from_file(filename)

    timestamps_no_none = {}
    # Remove none to enable easy sorting
    for (k,v) in timestamps.items():
        if(v.deq_start != None):
            timestamps_no_none[k] = v

    # Sort on deq_start (ascending)
    timestamps_sorted_on_deq = dict(sorted(timestamps_no_none.items(), key=lambda x: x[1].deq_start))

    # Save max_length first items from sorted dict
    timestamps_small = {k: v for i, (k, v) in enumerate(timestamps_sorted_on_deq.items()) if i < length} 

    
    # Prints used for confirming results
    print("timestamps dict length: ", len(timestamps_small))
    nr_deqs = 0
    nr_enqs = 0
    for ts in timestamps_small.values():
        if(ts.deq_start is not None): nr_deqs += 1
        if(ts.enq_start is not None): nr_enqs += 1
    print("Nr deqs: ", nr_deqs)
    print("Nr enqs: ", nr_enqs)

    # Extract data to use for producing csv
    iterable_for_csv = []
    for (k,v) in timestamps_small.items(): # both enq and deq exists
        iterable_for_csv.append([0, k, "PUT", v.enq_start, v.enq_end])
        iterable_for_csv.append([0, k, "GET", v.deq_start, v.deq_end])

    # Create csv
    new_filename = "timestamps/" + "short-" + length_str + "-" + filename
    with open(new_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(iterable_for_csv)

    return new_filename

if __name__=="__main__":
    filename = sys.argv[1] # input file or measurement for plot mode
    length_str = sys.argv[2] # linearization method or plot mode
    create_short_file(filename, length_str)
