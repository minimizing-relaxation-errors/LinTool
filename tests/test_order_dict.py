
# TODO: Borde göra ett test som kollar att varje bestämd order faktiskt finns som alternativ i original_dict
def test_if_valid(original_dict, solution_dict):
    # Equal length (checks if any values don't get assigned an order)    
    # This also checks that: Each key has only one order assigned (per operation)
    # TODO: Might break depending on how we decide to handle None
    o_dict_length = len(original_dict)
    s_dict_length = len(solution_dict)
    if(o_dict_length != s_dict_length): print("TEST Failed!\nOriginal dict length: ", o_dict_length, "\nSolution dict length: ", s_dict_length,"\n")
    else: print("TEST Passed: Equal lengths")
    
    # Each key has a tuple of size 2
    incorrect_keys = []
    for key, value in solution_dict.items():
        if len(value) != 2: incorrect_keys.extend(value)
    if(len(incorrect_keys) != 0): print("TEST Failed!\nKeys without 2-tuple: ", incorrect_keys,"\n")
    else: print("TEST Passed: All tuples size 2")

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
    if(len(e_multiple_orders) != 0): print("Test Failed!\nEnq orders assigned multiple times: ", e_multiple_orders,"\n")
    else: print("TEST Passed: Enq orders assigned once")
    if(len(e_multiple_orders) != 0): print("Test Failed!\nDeq orders assigned multiple times: ", d_multiple_orders,"\n")
    else: print("TEST Passed: Deq orders assigned once")
