# Interchange Linearization Method
# The idea behind this method is to start with a valid linearization and look for pairs of items
# whose enqueue points can be swapped to decrease the rank error sum of the two items.
# The swap must be valid; Both enqueue points must be within both intervals, and both
# dequeue points must be after the last enqueue point (ensures no item is dequeued before enqueueing after swap).

# NOTE: This method only swaps enqueue linerazation points (not dequeue)
# TODO: May be worth switching dequeue linearization points as well? 

import os
import sys

# Adds parent path to sys.path to enable importing script from neighbouring folder
# parent path is then removed to ensure relative paths can be used for later imports or file references
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_path)
from tests.test_timestamp_dict import test_timestamp_dict
sys.path.remove(parent_path)

# Global variables
order_data = {} # dictionary of item:[enq_index, deq_index]
lin = {}        # dictionary of item:[enq, deq]

# Expects as input: enqueue and dequeue index of an item
# Returns: the rank error of the item
def get_item_rank_error(this_e_ind, this_d_ind):
    rank_error = 0
    for item_inds in order_data.values():
        if item_inds[0] < this_e_ind and item_inds[1] > this_d_ind: rank_error += 1 # inds[0] is enq index and ind[1] is deq index
    return rank_error

# Checks if two elements can be swapped, if they can, it returns the potential rank error improvement
# Expects as input: two items, and start_end_timesatmps as dictionary of item:Timestamp
# Returns:  None if item1 and item2 are the same item or their enqueue linearization points cannot be swapped
#           A value for the improvement of swapping these two items (positive value is means there is improvement)
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

    # Get rank error for current order
    item1_re_before = get_item_rank_error(order_data[item1][0], order_data[item1][1])
    item2_re_before = get_item_rank_error(order_data[item2][0], order_data[item2][1])

    # Get rank error for swapped enqueue positions
    item1_re_after = get_item_rank_error(order_data[item2][0], order_data[item1][1])
    item2_re_after = get_item_rank_error(order_data[item1][0], order_data[item2][1])

    return (item1_re_before + item2_re_before) - (item1_re_after + item2_re_after)

# Swaps enqueue linearization points
# Expects as input: two items
# Assumes the two items can be swapped (with regard to their enqueue interval)
# NOTE: Updates global variables lin and order_data
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

# Expects as input: a dictionary of item:Timestamp
def get_total_last_timestamp(start_end_timestamps):
    last_timestamp = 0
    for (k, v) in start_end_timestamps.items():
        if v.enq_end > last_timestamp: last_timestamp = v.enq_end
        if v.deq_end != None:
            if v.deq_end > last_timestamp: last_timestamp = v.deq_end
    return last_timestamp

# Sets all dequeue lin points (for items with dequeue None) to last possible timestamp
# Expects as input: start_end_timestamps as a dictionary of item:Timestamp, last timestamp 
#                   and lin as a dictionary item:[enq_timestamp, deq_timestamp]
def set_deq_none_last(start_end_timestamps, original_last_timestamp, lin):
    # Pre-compute: 
    last_timestamp = original_last_timestamp
    for (k,v) in start_end_timestamps.items():
        if v.deq_start is None:
            lin[k][1] = last_timestamp+1 # Set deq timestamp in existing_lin to one after all others
            last_timestamp += 1
    return lin

# Expects as input: existing_lin as a dictionary of item:[enq timestamp, deq timestamp],
#                   start_end_timestamps as a dictionary of item:Timestamp,
#                   number of iterations,
#                   number of swaps last iterations which will stop the loop before the next iteration
# NOTE: start_end_timestamps is never altered
def interchange(existing_lin, start_end_timestamps, nr_iterations, nr_swaps_stopping_criteria):
    
    ###### SET GLOBAL VARIABLES
    # Set lin
    global lin
    original_last_timestamp = get_total_last_timestamp(start_end_timestamps)
    lin = set_deq_none_last(start_end_timestamps, original_last_timestamp, existing_lin)

    # Set order_data item:[enq_index, deq_index]
    # Determines indices in total order for enqueues and dequeues respectively
    # Assumes there are at least as many enqueues as dequeues
    global order_data
    items_sorted_on_enq = [ k for k, v in sorted(lin.items(), key=lambda item: item[1][0]) ] # item[1][0] is enqueue timestamp
    items_sorted_on_deq = [ k for k, v in sorted(lin.items(), key=lambda item: item[1][1]) ] # item[1][1] is dequeue timestamp
    for index, item in enumerate(items_sorted_on_enq):
        order_data[item] = [index, None]
    for index, item in enumerate(items_sorted_on_deq):
        order_data[item][1] = index

    ###### MAIN LOOP
    count = 0
    while count < nr_iterations and count < nr_swaps_stopping_criteria: 
        nr_swaps_this_iteration = 0
        # Store potential swaps: (TODO: Optimize if possible. Takes an awful lot of time to run)
        pot_swaps = {} # item:[(item to swap, rank error improvement)]
        for item1 in lin.keys():
            for item2 in lin.keys():
                re_imp = get_rank_error_improvement(item1, item2, start_end_timestamps)
                if re_imp == None: continue 
                elif re_imp > 0: 
                    if item1 in pot_swaps.keys():
                        pot_swaps[item1].append((item2, re_imp))
                    else:
                        pot_swaps.update({item1:[(item2, re_imp)]})

        # Execute swaps 
        # For each item, executes the best potential swap available
        # Ignores potential swaps that contain items that were already swapped this iteration
        has_been_swapped = [] 
        for (item1, item_list) in pot_swaps.items():
            if item1 in has_been_swapped: continue
            best_imp = (None, 0) # Item with best improvement
            for (item2, re_imp) in item_list:
                if item2 in has_been_swapped: continue
                if re_imp > best_imp[1]: best_imp = (item2, re_imp) 
            if best_imp[0] != None:
                swap_items(item1, best_imp[0]) # Swap items
                has_been_swapped.extend([best_imp[0], item1]) # Mark both items as having been swapepd
                nr_swaps_this_iteration += 1
        
        count += 1
        print("Finished iteration ", count, " with ", nr_swaps_this_iteration, " swaps")
    
    ###### OUTPUT DATA
    puts = {}   # item:timestamp
    gets = {}
    for (item,lin_list) in lin.items():
        puts[item] = lin_list[0]
        if lin_list[1] <= original_last_timestamp:
            gets[item] = lin_list[1]             # Only save dequeue timestamp if they were not None originally

    test_timestamp_dict(puts, gets, start_end_timestamps) # TODO: Consider if tests should be done here or in linearization_tool
    
    print("PUTS: ", len(puts), " GETS: ", len(gets))
    return (puts, gets)