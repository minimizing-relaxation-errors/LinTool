''' SCRIPT DESCRIPTION: Interchange Linearization Method
This method starts with a valid linearization and swaps the linearization points of favorable pairs.
Iteratively optimizes the linearization.
'''
import os
import sys
import datetime
from enum import Enum, auto 

class Op(Enum):  # TODO: Maybe move out
    Enq = auto()
    Deq = auto()

# Global variables
lin = {}                # dictionary of item:[enq, deq]
overlapping_items = {}  # dictionary of item:[items overlapping in enqueue/dequeue interval] (depending on which init function is called)

# Expects as input: existing_lin as a dictionary of item:[enq timestamp, deq timestamp],
#                   start_end_timestamps as a dictionary of item:Timestamp,
#                   number of iterations,
#                   stopping critera as number of swaps executed last iteration
# NOTE: start_end_timestamps is never altered
def interchange(existing_lin, start_end_timestamps, nr_iterations, nr_swaps_stopping_criteria):
    original_last_timestamp = get_total_last_timestamp(start_end_timestamps)
    init_lin(start_end_timestamps, existing_lin, original_last_timestamp)

    ###### Optimize enqueue linearization points
    init_overlapping(Op.Enq, start_end_timestamps)
    start_t = datetime.datetime.now() # Start timing first iteration
    pot_swaps = init_pot_swaps(start_end_timestamps, Op.Enq) # pot_swaps is item1:[(item2, re_imp)]

    out_str = ""

    out_str += "ENQUEUE OPTIMIZATION \n"
    initial_tot_rank_error = get_total_rank_error(original_last_timestamp)
    out_str += "Initial total rank error: " + str(initial_tot_rank_error)
    count = 0
    while count < nr_iterations: 
        if count != 0: start_t = datetime.datetime.now()                            
        (pot_swaps, nr_swaps_this_iteration) = execute_and_update(pot_swaps, start_end_timestamps, Op.Enq) 
        count += 1
        # Prepare output prints:
        tot_rank_error = get_total_rank_error(original_last_timestamp)
        end_t = datetime.datetime.now()
        tmp_out_str =  ("ITERATION " + str(count) + ":\n" +
                    "Nr swaps this iteration: " + str(nr_swaps_this_iteration) + "\n" +
                    "Time (min): " + get_minutes_str(start_t, end_t) + "\n" +
                    "Total rank error after: " + str(tot_rank_error) + "\n")
        print(tmp_out_str)
        out_str += tmp_out_str
        # Check if stopping critera achieved
        if nr_swaps_stopping_criteria != None:
            if nr_swaps_this_iteration <= nr_swaps_stopping_criteria: break

    ###### Optimize Dequeue linearization points
    init_overlapping(Op.Deq, start_end_timestamps)
    start_t = datetime.datetime.now() # Start timing first iteration
    pot_swaps = init_pot_swaps(start_end_timestamps, Op.Deq) # pot_swaps is item1:[(item2, re_imp)]
    out_str += "\nDEQUEUE OPTIMIZATION \n"
    count = 0
    while count < nr_iterations: 
        if count != 0: start_t = datetime.datetime.now() 
        (pot_swaps, nr_swaps_this_iteration) = execute_and_update(pot_swaps, start_end_timestamps, Op.Deq)
        count += 1
        # Prepare output prints:
        tot_rank_error = get_total_rank_error(original_last_timestamp)
        end_t = datetime.datetime.now()
        tmp_out_str = ("ITERATION " + str(count) + ":\n" +
                    "Nr swaps this iteration: " + str(nr_swaps_this_iteration) + "\n" +
                    "Time (min): " + get_minutes_str(start_t, end_t) + "\n" +
                    "Total rank error after: " + str(tot_rank_error) + "\n")
        print(tmp_out_str)
        out_str += tmp_out_str
        # Check if stopping criteria achieved
        if nr_swaps_stopping_criteria != None:
            if nr_swaps_this_iteration <= nr_swaps_stopping_criteria: break

    ###### OUTPUT DATA
    puts = {}  
    gets = {}
    for (item,enq_deq) in lin.items():
        puts[item] = enq_deq[0]
        if enq_deq[1] <= original_last_timestamp:
            gets[item] = enq_deq[1]             # Only save dequeue timestamp if they were not None originally

    return (puts, gets, out_str)

def get_minutes_str(start, end):
    return str(round(((end-start) / datetime.timedelta(microseconds=1))/(60 * 1000000),4))

# Returns the last interval ending (last possible timestamp)
def get_total_last_timestamp(start_end_timestamps):
    last_timestamp = 0
    for (k, v) in start_end_timestamps.items():
        if v.enq_end > last_timestamp: last_timestamp = v.enq_end
        if v.deq_end != None:
            if v.deq_end > last_timestamp: last_timestamp = v.deq_end
    return last_timestamp

# Simulates a timestamps for dequeue operations with no linearization point in the existing lin,
# by setting them to a timestamp after any other dequeue linearzation point
def init_lin(start_end_timestamps, existing_lin, original_last_timestamp):
    # Set lin
    last_timestamp = original_last_timestamp
    for (k,v) in start_end_timestamps.items():
        if v.deq_start is None:
            existing_lin[k][1] = last_timestamp+1 # Set deq timestamp in existing_lin to one after all others
            last_timestamp += 1
    global lin
    lin = existing_lin

# For each item, stores all items for which intervals overlap (with regard to the operation op_type)
def init_overlapping(op_type, start_end_timestamps):
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

# Computes total rank error for the linearization
# NOTE: For some reason computes a slightly lower rank error than it actually is. Insignificant difference.
def get_total_rank_error(original_last_timestamp):
    tot_re = 0
    for item1, (e1, d1) in lin.items():
        if lin[item1][1] > original_last_timestamp: continue  # Ignore nonexistant dequeues
        for item2, (e2, d2) in lin.items(): 
            if e2 < e1 and d2 > d1: 
                tot_re += 1 # item2 causes one rank error for item1
    return tot_re

# Computes rank error for a single item
def get_item_rank_error(this_e_ind, this_d_ind):
    rank_error = 0
    for (e,d) in lin.values():
        if e < this_e_ind and d > this_d_ind: rank_error += 1 # inds[0] is enq index and ind[1] is deq index
    return rank_error

# Returns the rank error improvement of swapping two items (returns None if swap is invalid)
# NOTE: Does not actually execute the swap. Does not alter lin
def get_rank_error_improvement(item1, item2, start_end_timestamps, op_type):
    # If item1 and item2 are the same, then no point in swapping
    if item1 == item2: return None

    item1_enq = lin[item1][0]
    item1_deq = lin[item1][1]
    item2_enq = lin[item2][0]
    item2_deq = lin[item2][1]

    # If either deq linearization point is before the other's enqueue linearization point, then swap is not possible
    if item1_deq < item2_enq or item2_deq < item1_enq: return None

    # Get rank error for current linearization
    item1_re_before = get_item_rank_error(lin[item1][0], lin[item1][1])
    item2_re_before = get_item_rank_error(lin[item2][0], lin[item2][1])
    
    match op_type:
        case Op.Enq:
            # If either enq linearization point is outside the other's interval, swap is not possible
            if start_end_timestamps[item1].enq_start > item2_enq or start_end_timestamps[item1].enq_end < item2_enq: return None
            if start_end_timestamps[item2].enq_start > item1_enq or start_end_timestamps[item2].enq_end < item1_enq: return None
            # Get rank error for swapped enqueue positions
            item1_re_after = get_item_rank_error(lin[item2][0], lin[item1][1])
            item2_re_after = get_item_rank_error(lin[item1][0], lin[item2][1])
        case Op.Deq:
            # If either deq linearization point is outside the other's interval, swap is not possible
            if start_end_timestamps[item1].deq_start == None or start_end_timestamps[item2].deq_start == None: return None # If either dequeue value None
            if start_end_timestamps[item1].deq_start > item2_deq or start_end_timestamps[item1].deq_end < item2_deq: return None
            if start_end_timestamps[item2].deq_start > item1_deq or start_end_timestamps[item2].deq_end < item1_deq: return None
            # Get rank error for swapped dequeue positions
            item1_re_after = get_item_rank_error(lin[item1][0], lin[item2][1])
            item2_re_after = get_item_rank_error(lin[item2][0], lin[item1][1])
    # Returns improvement (can be negative)
    return (item1_re_before + item2_re_before) - (item1_re_after + item2_re_after)

# Swaps item1's and item2's linearization point (of operation op_type) 
# Assumes the two items can be swapped (with regard to their enqueue interval)
# NOTE: Updates global variables lin
def swap_items(item1, item2, op_type):
    global lin
    match op_type:
        case Op.Enq:
            # Swap enqueue timestamp
            item1_enq = lin[item1][0]
            lin[item1][0] = lin[item2][0]
            lin[item2][0] = item1_enq
        case Op.Deq:
            # Swap dequeue timestamp
            item1_deq = lin[item1][1]
            lin[item1][1] = lin[item2][1]
            lin[item2][1] = item1_deq

# Updates pot_swap[item_a] with the pot_swap[item_b] and swaps out its own occurence with item_b 
# Returns updated pot_swaps
def update_a_with_bs_list(item_a, item_b, pot_swaps, start_end_timestamps, op_type):
    new_list = []
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
# Ignores items that have been swapped this iteration
def execute_and_update(pot_swaps, start_end_timestamps, op_type):
    nr_swaps_this_iteration = 0
    has_been_swapped = [] # TODO:Set?
    for item1, item1_list in pot_swaps.items(): # TODO: Feels like we should need to update overlapping_items
        if item1 in has_been_swapped: continue
        best_imp = (None, 0)
        for (item2, re_imp) in item1_list: 
            if item2 in has_been_swapped: continue 
            if re_imp > best_imp[1]: best_imp = (item2, re_imp)
        if best_imp[0] != None:
            swap_items(item1, best_imp[0], op_type)

            has_been_swapped.extend([best_imp[0], item1]) # Mark both items as swapped
            nr_swaps_this_iteration += 1

            # Update pot_swaps:
            # Swap the two item's potential swap lists, and account for their own occurence in the respective list
            pot_swaps = update_a_with_bs_list(item1, best_imp[0], pot_swaps, start_end_timestamps, op_type)
            pot_swaps = update_a_with_bs_list(best_imp[0], item1, pot_swaps, start_end_timestamps, op_type)

            # Update all other items' potential swap lists
            pot_swaps = update_other_a_lists_with_b(item1, best_imp[0], pot_swaps, start_end_timestamps, op_type)
            pot_swaps = update_other_a_lists_with_b(best_imp[0], item1, pot_swaps, start_end_timestamps, op_type)
    return (pot_swaps, nr_swaps_this_iteration)