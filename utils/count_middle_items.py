# This is a utility script to count the number of items between pairs which could be swapped
# and to confirm that a swap cannot negatively impact them.
# The script is used to reason about why/how the Interchange method works
# Lots of copy paste:d code from the interchange method code


''' SCRIPT DESCRIPTION: Interchange Linearization Method
This method starts with a valid linearization and swaps the linearization points of favorable pairs.
Iteratively optimizes the linearization.
'''
import os
import sys
import datetime
from enum import Enum, auto 

parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Cursed
sys.path.append(parent_path)
from utils.timestamp_from_file import get_existing_lin, get_timestamps_from_file
sys.path.remove(parent_path)

class Op(Enum):  # TODO: Maybe move out
    Enq = auto()
    Deq = auto()

# Global variables
lin = {}                # dictionary of item:[enq, deq]
overlapping_items = {}  # dictionary of item:[items overlapping in enqueue/dequeue interval] (depending on which init function is called)
order_data = {}         # dictionary of item:[enq_order, deq_order] TODO: Should probably be removed

def check_middle_items(existing_lin, start_end_timestamps):
    original_last_timestamp = get_total_last_timestamp(start_end_timestamps)
    init_lin(start_end_timestamps, existing_lin, original_last_timestamp)

    init_overlapping(Op.Deq, start_end_timestamps)
    pot_swaps = init_pot_swaps(start_end_timestamps, Op.Deq) # pot_swaps is item1:[(item2, re_imp)]

    print("-------------------------------------------------")
    init_order_data()
    (items_between_both_enq_deq, nr_pairs_with_problematic_items_between) = get_items_between_both_enq_deq(pot_swaps) 
    nr_middle_items = 0
    for item, pair_list in items_between_both_enq_deq.items():
        nr_middle_items += len(pair_list)
    print("Number of items between both deq and enq: ", nr_middle_items, " distributed over ", nr_pairs_with_problematic_items_between, " pairs\n")
    nr_pot_swaps = 0
    for item1, list1 in pot_swaps.items():
        for item2, re_imp in list1:
            nr_pot_swaps += 1
    print("Number of potential swaps: ", nr_pot_swaps, "\n")

    nr_neg = 0
    swapped_items = []
    for item1,pair_list in items_between_both_enq_deq.items():
        item1_re_before = get_item_rank_error(lin[item1][0], lin[item1][1], lin)
        for (item2, item3) in pair_list:
            if (item2 in swapped_items) or (item3 in swapped_items): continue
            new_lin = swap_items(item2, item3, Op.Deq)
            swapped_items.append(item2)
            swapped_items.append(item3)
            item1_re_after = get_item_rank_error(new_lin[item1][0], new_lin[item1][1], new_lin)
            if item1_re_before - item1_re_after < 0:
                nr_neg += 1
    print("nr neg: ", nr_neg)


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

# Computes rank error for a single item
def get_item_rank_error(this_e, this_d, current_lin):
    rank_error = 0
    for (e,d) in current_lin.values():
        if e < this_e and d > this_d: rank_error += 1 
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
    item1_re_before = get_item_rank_error(lin[item1][0], lin[item1][1], lin)
    item2_re_before = get_item_rank_error(lin[item2][0], lin[item2][1], lin)
    
    match op_type:
        case Op.Enq:
            # If either enq linearization point is outside the other's interval, swap is not possible
            if start_end_timestamps[item1].enq_start > item2_enq or start_end_timestamps[item1].enq_end < item2_enq: return None
            if start_end_timestamps[item2].enq_start > item1_enq or start_end_timestamps[item2].enq_end < item1_enq: return None
            # Get rank error for swapped enqueue positions
            item1_re_after = get_item_rank_error(lin[item2][0], lin[item1][1], lin)
            item2_re_after = get_item_rank_error(lin[item1][0], lin[item2][1], lin)
        case Op.Deq:
            # If either deq linearization point is outside the other's interval, swap is not possible
            if start_end_timestamps[item1].deq_start == None or start_end_timestamps[item2].deq_start == None: return None # If either dequeue value None
            if start_end_timestamps[item1].deq_start > item2_deq or start_end_timestamps[item1].deq_end < item2_deq: return None
            if start_end_timestamps[item2].deq_start > item1_deq or start_end_timestamps[item2].deq_end < item1_deq: return None
            # Get rank error for swapped dequeue positions
            item1_re_after = get_item_rank_error(lin[item1][0], lin[item2][1], lin)
            item2_re_after = get_item_rank_error(lin[item2][0], lin[item1][1], lin)
    # Returns improvement (can be negative)
    return (item1_re_before + item2_re_before) - (item1_re_after + item2_re_after)

# Swaps item1's and item2's linearization point (of operation op_type) 
# Assumes the two items can be swapped (with regard to their enqueue interval)
# NOTE: Updates global variables lin 
def swap_items(item1, item2, op_type):
    new_lin = lin
    match op_type:
        case Op.Enq:
            # Swap enqueue timestamp
            #print("before: ", new_lin[item1], new_lin[item2])
            item1_enq = new_lin[item1][0]
            new_lin[item1][0] = new_lin[item2][0]
            new_lin[item2][0] = item1_enq
        case Op.Deq:
            # Swap dequeue timestamp
            item1_deq = new_lin[item1][1]
            new_lin[item1][1] = new_lin[item2][1]
            new_lin[item2][1] = item1_deq
    return new_lin

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

# NOTE: order_data only used for checking items between, not actual computations. Could be removed.
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

# NOTE: only checks items between, no actual computations. Could be removed.
# Is used to see how many items have enq points between pairs' enq points AND deq points between pairs' deq points
def get_items_between_both_enq_deq(pot_swaps):
    items_between_both_enq_deq = {}
    nr_pairs_with_problematic_items_between = 0
    items_sorted_on_enq = {points[0]:item for (item,points) in sorted(order_data.items(), key=lambda item: item[1][0]) if points} # Unecessary for just counting, but oh well
    items_sorted_on_deq =  {points[1]:item for (item,points) in sorted(order_data.items(), key=lambda item: item[1][1]) if points}

    pairs_considered = []
    for item1, item1_list in pot_swaps.items():
        (e1,d1) = order_data[item1]
        for item2, re_imp in item1_list:
            if item1 == item2: continue
            (e2,d2) = order_data[item2]
            skip = False # Just to make it skip pairs already considered
            for (i1,i2) in pairs_considered:
                if (i1 == item1 and i2 == item2) or (i1 == item2 and i2 == item1): 
                    skip = True
                    break
            if skip: continue
            pairs_considered.append((item1,item2))
            count = 0
            for i in range(min(e1,e2)+1, max(e1,e2)): # exclude endpoints for this proof of concept (they belong to the pair)
                e_item = items_sorted_on_enq[i]
                for j in range(min(d1,d2)+1, max(d1,d2)):
                    d_item = items_sorted_on_deq[j]
                    if e_item == d_item: 
                        if e_item in items_between_both_enq_deq.keys():
                            count += 1
                            items_between_both_enq_deq[e_item].append([(item1,item2)])
                        items_between_both_enq_deq[e_item] = [(item1, item2)]
            if count > 0:
                nr_pairs_with_problematic_items_between += 1
    return items_between_both_enq_deq, nr_pairs_with_problematic_items_between



if __name__=="__main__":
    filename = sys.argv[1]
    check_middle_items(get_existing_lin(filename), get_timestamps_from_file(filename))