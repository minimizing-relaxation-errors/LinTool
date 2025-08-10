# NOTE: As of changes 2025-05-28, we have not tested on a failing file, hence we have not seen what out_str looks like
# Takes as input    original_dict which an order dict item:([enq ordering], [deq ordering])
#                   and solution dict which is an item:(enq order, deq order)
def test_if_order_valid(original_dict, solution_dict):
    out_str = ""
    passed_all = True
    # Equal length (checks if any values don't get assigned an order)    
    # This also checks that: Each key has only one order assigned (per operation)
    # NOTE: Might break depending on how we decide to handle None
    o_dict_length = len(original_dict)
    s_dict_length = len(solution_dict)
    if(o_dict_length != s_dict_length): 
        out_str += ("\nFAILED Test: Equal lengths\nOriginal dict length: " + str(o_dict_length) + 
                    "\nSolution dict length: " + str(s_dict_length),"\n")
        passed_all = False
    else: out_str += "\nPASSED Test: Equal lengths"
        
    # Check that each decided order is a valid order in original_dict
    nr_not_in_original_dict = 0
    for item,(e,d) in solution_dict.items():
        if not e in original_dict[item][1]: nr_not_in_original_dict += 1
        if not d in original_dict[item][2]: nr_not_in_original_dict += 1
    if nr_not_in_original_dict > 0:
        out_str +=  "\nFAILED Test: Orders in original dict, " + str(nr_not_in_original_dict)
        passed_all = False
    else: 
        out_str += "\nPASSED Test: Orders in original dict"
    
    # Each key has a tuple of size 2
    incorrect_keys = []
    for key, value in solution_dict.items():
        if len(value) != 2: incorrect_keys.extend(value)
    if(len(incorrect_keys) != 0): 
        out_str += "\nFAILED Test: All tuples size 2\nNumber of keys without 2-tuple: " + str(len(incorrect_keys)) + "\n"
        passed_all = False
    else: 
        out_str += "\nPASSED Test: All tuples size 2"

    # Order assigned once
    e_multiple_orders = []
    d_multiple_orders = []
    for e1, d1 in solution_dict.values():
        e_occ = 0
        d_occ = 0
        for e2, d2 in solution_dict.values():
            if e1 == e2: e_occ += 1
            if d1 == d2: d_occ += 1
        if e_occ > 1: e_multiple_orders.append(e1)
        if d_occ > 1: d_multiple_orders.append(d1)
    if(len(e_multiple_orders) != 0): 
        out_str += "\nFAILED Test: Enq orders assigned once\nNumber of enq orders assigned multiple times: " + str(len(e_multiple_orders)) + "\n"
        passed_all = False
    else: 
        out_str += ("\nPASSED Test: Enq orders assigned once")
    if(len(e_multiple_orders) != 0): 
        out_str += ("\nFAILED Test: Deq orders assigned once\nNumber of deq orders assigned multiple times: " + str(len(d_multiple_orders)) + "\n")
        passed_all = False
    else: out_str += ("\nPASSED Test: Deq orders assigned once")

    return (passed_all, out_str)
