# take existing linearization and start/end timestamp

# create some structure for timestamps with rank error saved. 
# maybe also nr of values enqueued before but dequeued after (or could utilize ordering reduction and do simple swap methods)

# possible approach: start with operation with highest max rank error
# move forward or back (within its interval)

# NOTE: This method only tries to swaps enqueue positions (not dequeue)

# Idea behind the method:
#   Start with a valid linearization
#   Look for items which can be swapped to get a lower total rank error between the two items (check that it creates a valid linearization as well)
#   Since the rest of the linearization is valid and predetermined, swapping the items will only affect their rank errors(???)
#   since both items must be dequeued after the last item's enqueue. ???? 


import datetime
import os
import sys

parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Cursed
sys.path.append(parent_path)
from tests.test_timestamp_dict import test_timestamp_dict
sys.path.remove(parent_path)



# TODO: order_data has new shape! item:[enq_index, deq_index]



# Global variables. Maybe this is bad idk
# order_data is a dictionary of item:[enq_index, deq_index]
order_data = {}
# lin is a dictionary of item:[enq, deq]
lin = {}

# Expects list enqs_bef with all items enqueued before, and list deqs_bef with all items dequeued before
# Returns rank error for a single item specified by enqs_bef and deqs_bef
def get_item_rank_error(this_e_ind, this_d_ind):
    # WITH NEW STRUCTURE item(enq_index, deq_index)
    rank_error = 0
    for inds in order_data.values():
        if inds[0] < this_e_ind and inds[1] > this_d_ind: rank_error += 1 # inds[0] is enq index and ind[1] is deq index
    return rank_error
    # WITH OLD STRUCTURE:
    #rank_error = 0
    #if enqs_bef == None: return 0 # If first element, return 0
    #for e in enqs_bef:
    #    if deqs_bef == None: continue
    #    elif e not in deqs_bef: rank_error += 1
    #return rank_error

# This function tests if two elements can be swapped, if they can, it returns the potential rank error improvement

# Expects start_end_timesatmps as dictionary of item:Timestamp
# Returns None if item1 and item2 are the same item or their enqueue linearization points cannot be swapped
# Returns a value for the improvement of swapping these two items (positive value is means there is improvement)
# NOTE: Does not actually execute the swap. Does not alter order_data or lin
def get_rank_error_improvement(item1, item2, start_end_timestamps):
    # If item1 and item2 are the same, then no point in swapping
    if item1 == item2: return None

    # If either enq linearization point is outside the other's interval, swap is not possible
    item1_enq = lin[item1][0]
    item1_deq = lin[item1][1]
    item2_enq = lin[item2][0]
    item2_deq = lin[item2][1]
    if start_end_timestamps[item1].enq_start > item2_enq or start_end_timestamps[item1].enq_end < item2_enq: return None
    if start_end_timestamps[item2].enq_start > item1_enq or start_end_timestamps[item2].enq_end < item1_enq: return None
    # If either deq linearization point is before the other's enqueue linearization point, then swap is not possible
    if item1_deq < item2_enq or item2_deq < item1_enq: return None

    item1_re_before = get_item_rank_error(order_data[item1][0], order_data[item1][1])
    item2_re_before = get_item_rank_error(order_data[item2][0], order_data[item2][1])

    item1_re_after = get_item_rank_error(order_data[item2][0], order_data[item1][1]) # Enqueue positions swapped
    item2_re_after = get_item_rank_error(order_data[item1][0], order_data[item2][1])

    return (item1_re_before + item2_re_before) - (item1_re_after + item2_re_after)

# Assumes item1 and item2 can be swapped (with regard to their enqueue interval)
# Updates global variables lin and order_data
def swap_items(item1, item2):
    global lin
    global order_data
    # Swap enqueue timestamp
    item1_enq = lin[item1][0]
    lin[item1][0] = lin[item2][0]
    lin[item2][0] = item1_enq
    # Update order_data to match new enqueue indices
    item1_e_ind = order_data[item1][0]
    order_data[item1][0] = order_data[item2][0]
    order_data[item2][0] = item1_e_ind

# Expects start_end_timestamp as a dictionary of item:Timestamp
def get_total_last_timestamp(start_end_timestamps):
    last_timestamp = 0
    for (k, v) in start_end_timestamps.items():
        if v.enq_end > last_timestamp: last_timestamp = v.enq_end
        if v.deq_end != None:
            if v.deq_end > last_timestamp: last_timestamp = v.deq_end
    return last_timestamp

def set_deq_none_last(start_end_timestamps, lin):
    # Pre-compute: set all dequeue lin points (for items with dequeue None) to last possible timestamp
    print("Initiated: Pre-processing dequeue None")
    last_timestamp = get_total_last_timestamp(start_end_timestamps)
    for (k,v) in start_end_timestamps.items():
        if v.deq_start is None:
            lin[k][1] = last_timestamp+1 # Set deq timestamp in existing_lin to the last possible
            last_timestamp += 1
    print("Finished: Pre-processing dequeue None")
    return lin

# Expects existing_lin as a dictionary of item:(enq timestamp, deq timestamp)
# Expects start_end_timestamps as a dictionary of item:Timestamp
# start_end_timestamps is never altered
def interchange(existing_lin, start_end_timestamps, nr_iterations):

    #os.path.isfile(fname)
    # Set global variables
    #global lin
    #if(os.path.isfile("positions/" + filename)):
    #lin = time_positioning_pickle(filename)
    #global order_data
    #order_data = un_pickle("positions", filename)
    #print("Initiated: Setting global variables")
    #set_order_data()
    #print("Finished: Setting global variables")


    # Need to set lin and order_data. However, need to set dequeue None's to last timestamp BEFORE pickling order_data.

    # TODO: Currently, all precomputation is done in time_postioning.py. Need to have better structure.
    #       Best workflow corrently is to generate a pkl file manually. NOT IN CODE. Simply have the code assume the .pkl file exists.
    global lin, order_data
    lin = set_deq_none_last(start_end_timestamps, existing_lin) # TODO: This is done both here and in time_positioning.py because I can't figure out a better way to do it
    #order_data = un_pickle("positions", filename)

    print("Initiated: Setting index data")
    items_sorted_on_enq = [ k for k, v in sorted(lin.items(), key=lambda item: item[1][0]) ] # item[1][0] is enqueue timestamp
    items_sorted_on_deq = [ k for k, v in sorted(lin.items(), key=lambda item: item[1][1]) ] # item[1][1] is dequeue timestamp
    print("CHECK equal nr of enq as deq: ", len(items_sorted_on_enq) == len(items_sorted_on_deq))

    # GENERATE ORDER DATA item:[enq_index, deq_index]
    # Determines indices in total order for enqueues and dequeues respectively
    # Assumes there are at least as many enqueues as dequeues
    # Populate enqueue index:
    for index, item in enumerate(items_sorted_on_enq):
        order_data[item] = [index, None]

    for index, item in enumerate(items_sorted_on_deq):
        order_data[item][1] = index
    print("Finished: Setting index data")

    count = 0
    has_changed = True

    # Main loop:
    print("Initiated: Main loop")
    while count < nr_iterations and has_changed: # Want to stop when no more change is done
        has_changed = False
        nr_swaps_this_iteration = 0
        pot_swaps = {} # item:[(item to swap, rank error improvement)]
        print("Initiated: Storing potential swaps") # TODO: Optimize? This takes sooo long to run!
        print(datetime.datetime.now())
        for item in lin.keys():             # TODO: TRY TO CHANGE THIS BACK. Did not make it faster lol
            pot_swaps[item] = [] # Init values for each item to avoid having to check if item exists when assigning in next forloop. THIS IS PROBABLY BAD but before, it took SOOo long to run with the update check
        for item1 in lin.keys():
            for item2 in lin.keys():
                re_imp = get_rank_error_improvement(item1, item2, start_end_timestamps)
                if re_imp == None: continue 
                elif re_imp > 0: 
                    pot_swaps[item1].append((item2, re_imp)) # Positive improvement is good. Not tested, may give some list error
        print(datetime.datetime.now())
        print("Finished: Storing potential swaps. pot_swaps length: ", len(pot_swaps))

        # Handle pot_swaps
        print("Initiated: Checking potential swaps and swapping")
        has_been_swapped = [] # TODO: Maybe change. This is instead of actually popping items from the dictionary.
        for (item1,item_list) in pot_swaps.items():
            if item1 in has_been_swapped: continue
            best_imp = (None, 0)
            for (item2, re_imp) in item_list:
                if item2 in has_been_swapped: continue
                if re_imp > best_imp[1]: best_imp = (item2, re_imp)
            if best_imp[0] != None:
                swap_items(item1, best_imp[0]) # Swap items
                has_changed = True
                has_been_swapped.extend([best_imp[0], item1]) # Mark both items as having been swapepd
                nr_swaps_this_iteration += 1 # TODO: Remove
        print("Initiated: Checking potential swaps and swapping. Number of swaps this iteration: ", nr_swaps_this_iteration)
        if(not has_changed): print("Will exit main loop after iteration: ", count)
        count += 1
    print("Finished: Main loop")

    print("Status has_changed: ", has_changed)

    print("Initiated: Defining output data")
    # Define output data
    puts = {}   # item:timestamp
    gets = {}
    for (item,lin_list) in lin.items():
        puts[item] = lin_list[0]
        gets[item] = lin_list[1]
    print("Finished: Defining output data")

    test_timestamp_dict(puts, gets, start_end_timestamps)
    


    return (puts, gets)