import csv
import sys
import os

parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Cursed
sys.path.append(parent_path)
from linearization_tool import get_existing_lin, get_timestamps_from_file
sys.path.remove(parent_path)

# NOTE: This script assumes that there exists 
#       1) a short interval file named "short-nr_items-filename" (in folder "timestamps")
#       2) an existing longer linearization file named <filename> (in folder "current_linearization_results")

# Takes from command line: <file name> <desired nr of items>
# Creates another .csv file (in current_linearization_results) named "short-nr_items-filename"
# which contains the existing linearization points of the items that are in the short interval file
def create_short_lin_file(filename, nr_items):

    interval_timestamps = get_timestamps_from_file("short-" + nr_items + "-" + filename) # dictionary of item:Timestamp

    lin_timestamps = get_existing_lin(filename) # dictionary of structure item:[enq_timestamp, deq_timestamp]

    # Extract data to use for producing csv
    iterable_for_csv = []
    for k in interval_timestamps.keys(): # both enq and deq exists
        iterable_for_csv.append([0, k, "PUT", lin_timestamps[k][0]])
        iterable_for_csv.append([0, k, "GET", lin_timestamps[k][1]])

    # Create csv
    new_filename = "current_linearization_results/" + "short-" + nr_items + "-" + filename
    with open(new_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(iterable_for_csv)

    return new_filename

if __name__=="__main__":
    filename = sys.argv[1] # input file or measurement for plot mode
    nr_items = sys.argv[2] # desired nr of items
    create_short_lin_file(filename, nr_items)
