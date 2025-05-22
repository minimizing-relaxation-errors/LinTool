# Interchange Linearization Method
# The idea behind this method is to start with a valid linearization and look for pairs of items
# whose enqueue points can be swapped to decrease the rank error sum of the two items.
# The swap must be valid; Both enqueue points must be within both intervals, and both
# dequeue points must be after the last enqueue point (ensures no item is dequeued before enqueueing after swap).

# NOTE: This method only swaps enqueue linerazation points (not dequeue)
# TODO: May be worth switching dequeue linearization points as well? Yes!

import os
import sys
import datetime
from enum import Enum, auto 

# Adds parent path to sys.path to enable importing script from neighbouring folder
# parent path is then removed to ensure relative paths can be used for later imports or file references
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_path)
from tests.test_timestamp_dict import test_timestamp_dict
sys.path.remove(parent_path)

class Op(Enum): 
    Enq = auto()
    Deq = auto()

# Global variables
order_data = {} # dictionary of item:[enq_index, deq_index]
lin = {}        # dictionary of item:[enq, deq]
overlapping_items = {} # dictionary of item:[items overlapping in enqueue/dequeue interval] (depending on which init function is called)

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
def init_lin(start_end_timestamps, existing_lin, original_last_timestamp):
    # Set lin
    global lin
    last_timestamp = original_last_timestamp # TODO: CONSIDER JUST HANDING NONE EVERYWHERE 
    for (k,v) in start_end_timestamps.items():
        if v.deq_start is None:
            lin[k][1] = last_timestamp+1 # Set deq timestamp in existing_lin to one after all others
            last_timestamp += 1
    return lin

def init_overlapping(op_type, start_end_timestamps):
    # Set overlapping items (items overlapping in enqueue interval)
    global overlapping_items
    for item1, ts1 in start_end_timestamps.items():
        if op_type == Op.Enq:
            s1 = ts1.enq_start
            e1 = ts1.enq_end
        elif op_type == Op.Deq:
            s1 = ts1.deq_start
            e1 = ts1.deq_end
            if s1 == None: continue
        items = []
        for item2, ts2 in start_end_timestamps.items():
            if item1 == item2: continue
            if op_type == Op.Enq:
                s2 = ts2.enq_start
                e2 = ts2.enq_end
            elif op_type == Op.Deq:
                s2 = ts2.deq_start
                e2 = ts2.deq_end
            if s2 == None: continue
            if not (e2 < s1 or s2 > e1): 
                items.append(item2)
        if items: # Don't add if items is empty
            overlapping_items[item1] = items

def init_order_data():
    # Set order_data 
    # Determines indices in total order for enqueues and dequeues respectively
    # Assumes there are at least as many enqueues as dequeues
    global order_data
    items_sorted_on_enq = [ k for k, v in sorted(lin.items(), key=lambda item: item[1][0]) ] # item[1][0] is enqueue timestamp
    items_sorted_on_deq = [ k for k, v in sorted(lin.items(), key=lambda item: item[1][1]) ] # item[1][1] is dequeue timestamp
    for index, item in enumerate(items_sorted_on_enq):
        order_data[item] = [index, None]
    for index, item in enumerate(items_sorted_on_deq):
        order_data[item][1] = index

def check_if_swapped(item, has_been_swapped):
    for (item1, item2) in has_been_swapped:
        if item1 == item or item2 == item:
            return True
    return False

def get_total_rank_error(original_last_timestamp): # TODO: Maybe should be generic in compute_rank_error idk
    tot_re = 0
    for item1, (e1, d1) in order_data.items():
        if lin[item1][1] > original_last_timestamp: continue  # TODO: This is so stupid maybe I should just handle none values idk
        for item2, (e2, d2) in order_data.items():
            if e2 < e1 and d2 > d1: 
                tot_re += 1 # item2 causes one rank error for item1
            # TODO: Remove enqueue or something'''
    return tot_re

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
def get_rank_error_improvement(item1, item2, start_end_timestamps, op_type):
    # If item1 and item2 are the same, then no point in swapping
    if item1 == item2: return None

    item1_enq = lin[item1][0]
    item1_deq = lin[item1][1]
    item2_enq = lin[item2][0]
    item2_deq = lin[item2][1]

    # Get rank error for current order
    item1_re_before = get_item_rank_error(order_data[item1][0], order_data[item1][1])
    item2_re_before = get_item_rank_error(order_data[item2][0], order_data[item2][1])
    
    # If either deq linearization point is before the other's enqueue linearization point, then swap is not possible
    if item1_deq < item2_enq or item2_deq < item1_enq: return None

    match op_type:
        case Op.Enq:
            # If either enq linearization point is outside the other's interval, swap is not possible
            if start_end_timestamps[item1].enq_start > item2_enq or start_end_timestamps[item1].enq_end < item2_enq: return None
            if start_end_timestamps[item2].enq_start > item1_enq or start_end_timestamps[item2].enq_end < item1_enq: return None
            
            # Get rank error for swapped enqueue positions
            item1_re_after = get_item_rank_error(order_data[item2][0], order_data[item1][1])
            item2_re_after = get_item_rank_error(order_data[item1][0], order_data[item2][1])
        case Op.Deq:
            # If either deq linearization point is outside the other's interval, swap is not possible
            s1 = start_end_timestamps[item1].deq_start
            s2 = start_end_timestamps[item2].deq_start
            e1 = start_end_timestamps[item1].deq_end
            e2 = start_end_timestamps[item2].deq_end
            if s1 == None or s2 == None: return None # If either dequeue value None
            if s1 > item2_deq or e1 < item2_deq: return None
            if s2 > item1_deq or e2 < item1_deq: return None
            
            # Get rank error for swapped dequeue positions
            item1_re_after = get_item_rank_error(order_data[item1][0], order_data[item2][1])
            item2_re_after = get_item_rank_error(order_data[item2][0], order_data[item1][1])


    return (item1_re_before + item2_re_before) - (item1_re_after + item2_re_after)

# Swaps enqueue linearization points
# Expects as input: two items
# Assumes the two items can be swapped (with regard to their enqueue interval)
# NOTE: Updates global variables lin and order_data
def swap_items(item1, item2, op_type):
    global lin
    global order_data
    global overlapping_items
    match op_type:
        case Op.Enq:
            # Swap enqueue timestamp
            item1_enq = lin[item1][0]
            lin[item1][0] = lin[item2][0]
            lin[item2][0] = item1_enq
            # Update order_data to match new enqueue indices
            item1_e_ind = order_data[item1][0]
            order_data[item1][0] = order_data[item2][0]
            order_data[item2][0] = item1_e_ind
        case Op.Deq:
            # Swap dequeue timestamp
            item1_deq = lin[item1][1]
            lin[item1][1] = lin[item2][1]
            lin[item2][1] = item1_deq
            # Update order_data to match new dequeue indices
            item1_d_ind = order_data[item1][1]
            order_data[item1][1] = order_data[item2][1]
            order_data[item2][1] = item1_d_ind

# Updates pot_swap[item_a] with the pot_swap[item_b] and swaps out its own occurence with item_b 
# Returns updated pot_swaps
# TODO: Consider that it may set an empty list in pot_swaps? does that matter?
def update_a_with_bs_list(item_a, item_b, pot_swaps, start_end_timestamps, op_type):
    #old_list = pot_swaps[item_b] # TODO: Maybe this shouldn't be the items in pot_swap, but actually be overlapping items?
    new_list = []
    #for (item, old_re_imp) in old_list:
    for item in overlapping_items[item_b]:
        if item == item_a: item = item_b # Swap item_a with item_b in the list (since it will be assigned to item_a)
        new_re_imp = get_rank_error_improvement(item_a, item, start_end_timestamps, op_type)
        if new_re_imp != None and new_re_imp > 0:
            new_list.append((item, new_re_imp))
    pot_swaps[item_a] = new_list
    return pot_swaps

def update_other_a_lists_with_b(item_a, item_b, pot_swaps, start_end_timestamps, op_type):
    pot_swaps_items = pot_swaps.keys()
    for o_item in overlapping_items[item_a]: # All items which could possibly be swappable with a
        if o_item not in pot_swaps_items: continue
        new_list = pot_swaps[o_item]
        b_updated = False
        for tuple in pot_swaps[o_item]: # For loop only exists to identify item_a or item_b and update it
            item = tuple[0]
            if item == item_a or item == item_b:
                b_updated = item == item_b
                new_list.remove(tuple) # Remove old occurence of item_a or item_b
                new_re_imp = get_rank_error_improvement(item, o_item, start_end_timestamps, op_type)
                if new_re_imp != None and new_re_imp > 0:
                    new_list.append((item, new_re_imp)) # Add item_a if there is still improvement
        # Check if item_b should be included in the list
        if not b_updated:
            b_re_imp = get_rank_error_improvement(item_b, o_item, start_end_timestamps, op_type)
            if b_re_imp != None and b_re_imp > 0:
                new_list.append((item_b, b_re_imp))
        pot_swaps[o_item] = new_list
    return pot_swaps

# For each item, store all items for which a swap would improve the pair's total rank error
def init_pot_swaps(start_end_timestamps, op_type):
    pot_swaps = dict() # item:[(item to swap, rank error improvement)]
    for (item1, item1_list) in overlapping_items.items():
        pot_swaps_list = []
        for item2 in item1_list:
            re_imp = get_rank_error_improvement(item1, item2, start_end_timestamps, op_type)
            if re_imp != None and re_imp > 0: 
                pot_swaps_list.append((item2, re_imp))
        pot_swaps[item1] = pot_swaps_list
    return pot_swaps

# EXECUTE SWAPS
# For each item, executes the best potential swap available
# Ignores potential swaps that contain items that were already swapped this iteration
def execute_and_update(pot_swaps, start_end_timestamps, op_type):
    nr_swaps_this_iteration = 0
    has_been_swapped = [] # TODO:Set?
    for (item1, item_list) in pot_swaps.items():
        if check_if_swapped(item1, has_been_swapped): continue
        best_imp = (None, 0) # Item with best improvement
        for (item2, re_imp) in item_list:
            if check_if_swapped(item2, has_been_swapped): continue 
            if re_imp > best_imp[1]: best_imp = (item2, re_imp) 
        if best_imp[0] != None:
            swap_items(item1, best_imp[0], op_type) # Swap items
            has_been_swapped.append((best_imp[0], item1)) # Mark both items as having been swapepd
            nr_swaps_this_iteration += 1

            # Update pot_swaps:
            # Swap the two item's potential swap lists, and account for their own occurence in the respective list
            pot_swaps = update_a_with_bs_list(item1, best_imp[0], pot_swaps, start_end_timestamps, op_type)
            pot_swaps = update_a_with_bs_list(best_imp[0], item1, pot_swaps, start_end_timestamps, op_type)

            # Update all other items' potential swap lists
            pot_swaps = update_other_a_lists_with_b(item1, best_imp[0], pot_swaps, start_end_timestamps, op_type)
            pot_swaps = update_other_a_lists_with_b(best_imp[0], item1, pot_swaps, start_end_timestamps, op_type)
    return (pot_swaps, nr_swaps_this_iteration)

def get_minutes_str(start, end):
    return str(round(((end-start) / datetime.timedelta(microseconds=1))/(60 * 1000000),4))

# Expects as input: existing_lin as a dictionary of item:[enq timestamp, deq timestamp],
#                   start_end_timestamps as a dictionary of item:Timestamp,
#                   number of iterations,
#                   number of swaps last iterations which will stop the loop before the next iteration
# NOTE: start_end_timestamps is never altered
def interchange(existing_lin, start_end_timestamps, nr_iterations, nr_swaps_stopping_criteria):
    
    original_last_timestamp = get_total_last_timestamp(start_end_timestamps)
    init_lin(start_end_timestamps, existing_lin, original_last_timestamp)
    init_order_data()

    ###### Optimize ENqueue linearization points
    init_overlapping(Op.Enq, start_end_timestamps)
    print("TOTAL RANK ERROR: ", get_total_rank_error(original_last_timestamp)) # TODO: Remove (sanity check for now)
    start_t = datetime.datetime.now() # Start timing first iteration
    pot_swaps = init_pot_swaps(start_end_timestamps, Op.Enq) # pot_swaps is item1:[(item2, re_imp)]
    out_str = "ENQUEUE OPTIMIZATION \n"
    print("ENQUEUE OPTIMIZATION \n") # TODO: REMOVE
    count = 0
    while count < nr_iterations: 
        # Start timing iteration (all but the first)
        if count != 0: start_t = datetime.datetime.now() 
        # Execute swaps and update pot_swaps structure accordingly
        (pot_swaps, nr_swaps_this_iteration) = execute_and_update(pot_swaps, start_end_timestamps, Op.Enq)
        # Calculate total rank error to be printed in the output
        tot_rank_error = get_total_rank_error(original_last_timestamp)
        count += 1
        end_t = datetime.datetime.now()
        out_str += ("ITERATION " + str(count) + ":\n" +
                    "Nr swaps this iteration: " + str(nr_swaps_this_iteration) + "\n" +
                    "Time (min): " + get_minutes_str(start_t, end_t) + "\n" +
                    "Total rank error after: " + str(tot_rank_error) + "\n")
        tmp_str = ("ITERATION " + str(count) + ":\n" +  # TODO: REMOVE
                    "Nr swaps this iteration: " + str(nr_swaps_this_iteration) + "\n" +
                    "Time (min): " + get_minutes_str(start_t, end_t) + "\n" +
                    "Total rank error after: " + str(tot_rank_error) + "\n")
        print(tmp_str) # TODO: REMOVE
        if nr_swaps_stopping_criteria != None:
            if nr_swaps_this_iteration <= nr_swaps_stopping_criteria: break

    ###### Optimize DEqueue linearization points
    init_overlapping(Op.Deq, start_end_timestamps)
    print("TOTAL RANK ERROR: ", get_total_rank_error(original_last_timestamp)) # TODO: Remove (sanity check for now)
    start_t = datetime.datetime.now() # Start timing first iteration
    pot_swaps = init_pot_swaps(start_end_timestamps, Op.Deq) # pot_swaps is item1:[(item2, re_imp)]
    out_str = "DEQUEUE OPTIMIZATION \n"
    print("DEQUEUE OPTIMIZATION \n") # TODO: REMOVE
    count = 0
    while count < nr_iterations: 
        # Start timing iteration (all but the first)
        if count != 0: start_t = datetime.datetime.now() 
        # Execute swaps and update pot_swaps structure accordingly
        (pot_swaps, nr_swaps_this_iteration) = execute_and_update(pot_swaps, start_end_timestamps, Op.Deq)
        # Calculate total rank error to be printed in the output
        tot_rank_error = get_total_rank_error(original_last_timestamp)
        count += 1
        end_t = datetime.datetime.now()
        out_str += ("ITERATION " + str(count) + ":\n" +
                    "Nr swaps this iteration: " + str(nr_swaps_this_iteration) + "\n" +
                    "Time (min): " + get_minutes_str(start_t, end_t) + "\n" +
                    "Total rank error after: " + str(tot_rank_error) + "\n")
        tmp_str = ("ITERATION " + str(count) + ":\n" +  # TODO: REMOVE
                    "Nr swaps this iteration: " + str(nr_swaps_this_iteration) + "\n" +
                    "Time (min): " + get_minutes_str(start_t, end_t) + "\n" +
                    "Total rank error after: " + str(tot_rank_error) + "\n")
        print(tmp_str) # TODO: REMOVE
        if nr_swaps_stopping_criteria != None:
            if nr_swaps_this_iteration <= nr_swaps_stopping_criteria: break

    ###### OUTPUT DATA
    puts = {}   # item:timestamp
    gets = {}
    for (item,enq_deq) in lin.items():
        puts[item] = enq_deq[0]
        if enq_deq[1] <= original_last_timestamp:
            gets[item] = enq_deq[1]             # Only save dequeue timestamp if they were not None originally

    test_timestamp_dict(puts, gets, start_end_timestamps) # TODO: Consider if tests should be done here or in linearization_tool
    
    print("PUTS: ", len(puts), " GETS: ", len(gets))
    return (puts, gets, out_str)