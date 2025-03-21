import cvxpy as cp
import numpy as np
import math

from computeRankError import compute_rank_error
from linTry import exhaustive_ratio
from timestamp import Timestamp

# TODO: Document shit

# NOTE: 2025-03-20: Nu kör den, och jag har ett par basic tester för att se om outputten är rimlig.
#       Men den fungerar inte med window (fungerar helt utan window). 
#       Tar bara bort alla som redan valts från kommande potential positions. 
#       Men det gör att senare spans kan få NoneType error då orders/positions är helt tagna.


# NOTE: Overlap i Ides kod: Alla orders mellan enq och deq som är samma. Sen sorterar hon på det (färst till flest), kanske gör något liknande?

# TODO: Needs to consider deq None
# TODO: Needs to translate the ordering into a timestamp dictionary again

# TODO: Should probably try with test data that does not have too many overlapping at once


# TODO: Alternativ till att ta bort tagna indexes. Kanske gå igenom alla från start och ta bestäm för de som bara har en siffra.
#       Eller typ kolla alla som har <span antal att välja på och kör linear programming på dem??

span = 15500
step = 15500 # TODO: Shoudl try with step = span when the algorithm works. Might not make a difference in the results.
diff = span - step # must be positive probably

# TODO: Borde göra ett test som kollar att varje bestämd order faktiskt finns som alternativ i original_dict
def test_if_valid(original_dict, solution_dict):
    # Equal length (checks if any values don't get assigned an order)    
    # This also checks that: Each key has only one order assigned (per operation)
    # TODO: Might break depending on how I decide to handle None
    o_dict_length = len(original_dict)
    s_dict_length = len(solution_dict)
    length_test = o_dict_length == s_dict_length
    print("TEST Equal length: ", length_test)
    if(not length_test): print("Test failed!\nOriginal dict length: ", o_dict_length, "\nSolution dict length: ", s_dict_length,"\n")
    
    # Each key has a tuple of size 2
    incorrect_keys = []
    for key, value in solution_dict.items():
        if len(value) != 2: incorrect_keys.extend(value)
    key_tuple_test = len(incorrect_keys) == 0
    print("TEST Each key has a 2-tuple: ", key_tuple_test)
    if(not key_tuple_test): print("Test failed!\nKeys without 2-tuple: ", incorrect_keys,"\n")

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
    e_single_order_test = len(e_multiple_orders) == 0
    d_single_order_test = len(e_multiple_orders) == 0
    print("TEST Enq orders assigned once: ", e_single_order_test)
    if(not e_single_order_test): print("Test failed!\nEnq orders assigned multiple times: ", e_multiple_orders,"\n")
    print("TEST Deq orders assigned once: ", d_single_order_test)
    if(not d_single_order_test): print("Test failed!\nDeq orders assigned multiple times: ", d_multiple_orders,"\n")


# Expects ordering dict
def windowed_linear_programming(inp: dict):
    # TODO: I probably want to simply remove all dict entries with deq order list set to None
    #           OR JUST MAKE THEM INF
    # Parsing to handle None values
    total_length = len(inp)
    parsed_inp = {}
    count = 0
    for (key, (v1,v2)) in inp.items():
        if None in v2: 
            parsed_inp[key] = (v1,[total_length+count]) # orders are zero indexed. add order after those actually available to the other dequeues
            count += 1
        else: parsed_inp[key] = (v1, v2)

    # TODO: I LPn: kolla alla enq deq, om nån bara har 1 ordering, bestäm den. Gör det innan varje window LP
    #       Behöver nog sortera på antingen starttider eller typ färst till flest antal orderings
    #       Kanske ändra fönstret beroende på största antalet potential orderings

    start = 0
    list_values = list(parsed_inp.values())

    complete_enq_ordering = []
    complete_deq_ordering = []

    while start < total_length:
        # TODO: needs to be able to handle the last items which are maybe not evenly divisable with i

        end = start+span
        if(end > total_length): end = total_length                          # TODO: This is a bit funky. Perhaps it should simply optimize over the >= span final items. Since the last span otherwise just shrinks and does the optimization maybe uneccessarily at the end
        subset_list_values = [list_values[x] for x in range(start, end)]
        (decided_enq_ordering, decided_deq_ordering) = linear_programming_for_window(subset_list_values) # TODO: Do linear programming thing, decide the step first elements orderings
        print("Decided enq ordering: ", decided_enq_ordering)
        print("Decided deq ordering: ", decided_deq_ordering) 
        complete_enq_ordering.extend(decided_enq_ordering)  # TODO: Can probably just build solution dict right here and remove this code
        complete_deq_ordering.extend(decided_deq_ordering)

        #print(parsed_inp)

        # Remove the decided on orderings from the ENTIRE dict
        for (key, (v1,v2)) in parsed_inp.items():
            for item in complete_enq_ordering:
                if item in v1: parsed_inp[key] = (v1.remove(item), v2)
            for item in complete_deq_ordering:
                if item in v2: parsed_inp[key] = (v1, v2.remove(item))
        start += step

    # TODO: Do None check here
    print("Complete enq ordering: ", complete_enq_ordering)
    print("Complete deq ordering: ", complete_deq_ordering)

    # Build final output dict
    solution = {}
    for index, key in enumerate(parsed_inp):
        if(complete_deq_ordering[index] >= total_length): solution[key] = (complete_enq_ordering[index], None)
        else: solution[key] = (complete_enq_ordering[index], complete_deq_ordering[index])

    print(solution)


    test_if_valid(parsed_inp, solution)


    # TODO: Need to remake dict to actually output

# Expects an array A with n rows and m columns, outputs an array A with m rows and n columns
# Expects rows to be cvxpy-variables
def transpose(A):
    n = len(A)
    m = A[0].size
    transposed_A = [[None for _ in range(0,n)] for _ in range(0,m)] # n columns, m rows
    # Iterate A and add values to transposed_A
    for i in range(0, n):
        for j in range(0, m):
            transposed_A[j][i] = A[i][j]
    return transposed_A

# NOTE: Assumes all enqueues have dequeues
# inp_list is often of size span, but not always (at the end of dictionary)
def linear_programming_for_window(inp_list):
    enq_order_list = [inp_list[x][0] for x in range(0, len(inp_list))]
    deq_order_list = [inp_list[x][1] for x in range(0, len(inp_list))]
    #print("Deq order list: ", deq_order_list)
    nr_enqs = len(enq_order_list)
    enq_order_set = set()
    deq_order_set = set()

    # Consider each corresponding enq and deq order list
    for i in range(0, nr_enqs):
        enq_order_set.update(enq_order_list[i])
        deq_order_set.update(deq_order_list[i])

    # Array with potential orders (sorted, no duplicates)
    all_enq_orders = np.array(sorted(list(enq_order_set)))   # Detta är ganska cursed
    all_deq_orders = np.array(sorted(list(deq_order_set)))
    #print("All enq orders: ", all_enq_orders)
    #print("All deq orders: ", all_deq_orders)

    ######### CREATE CVXPY VARIABLES
    E = []
    D = []
    #print("Nr enqueues: ", nr_enqs)
    for i in range(0, nr_enqs):            
        #print("Length enq orders: ", len(all_enq_orders))
        #print("Length deq orders: ", len(all_deq_orders))
        E.append(cp.Variable(len(all_enq_orders), integer=True))
        D.append(cp.Variable(len(all_deq_orders), integer=True))

    ######### DEFINE CONSTRAINTS
    constraints = []
    for i in range(0, nr_enqs):
        constraints.append(E[i] >= 0) # Binary variables
        constraints.append(E[i] <= 1)
        constraints.append(D[i] >= 0)
        constraints.append(D[i] <= 1)

        this_enq_orders = enq_order_list[i] # Potential orderings for the current value's enqueue
        #print(this_enq_orders)
        this_deq_orders = deq_order_list[i]
        #print("This deq order", this_deq_orders)

        # Compare current value's enq/deq to all potential enq/deq orderings
        # If current value does not have any of them, set constraint that the corresponding variable must be 0 (cannot be chosen)
        for j in range(0, len(all_enq_orders)): 
            #print("This enqueue orders: ", this_enq_orders)
            #print("Current enq order: ", all_enq_orders[j])
            if(all_enq_orders[j] not in this_enq_orders): 
                #print(all_enq_orders[j], " not in ", this_enq_orders)
                #print("E[",i,"][",j,"] == 0")
                constraints.append(E[i][j] == 0)
        for j in range(0,len(all_deq_orders)):
            if (all_deq_orders[j] not in this_deq_orders):
                #print(all_deq_orders[j], " not in ", this_deq_orders)
                #print("D[",i,"][",j,"] == 0")
                constraints.append(D[i][j] == 0)
            #print()
        
        constraints.append(cp.sum(E[i]) == 1) # Each operation can only have a single order
        constraints.append(cp.sum(D[i]) == 1)

    #print(E)
    #print(D)
    transposed_E = transpose(E)
    transposed_D = transpose(D)
    #print(transposed_E)
    #print(transposed_D)

    #print("transposed length: ", len(transposed_E))
    #print("transposed[0] length: ", len(transposed_E[0]))

    for i in range(0, len(all_enq_orders)):
        #print("Iterating transposed: ", i)
        constraints.append(cp.sum(transposed_E[i]) <= 1) # Each order can only be "occupied" by a single operation (must be <= since there can be many more orders than operations in a sub solution)
    for i in range(0,len(all_deq_orders)):
        constraints.append(cp.sum(transposed_D[i]) <= 1)


    #print(constraints)

    ######### DEFINE OBJECTIVE FUNCTION
    potential_enq_order = np.array(E)
    potential_deq_order = np.array(D)
    """print("Potential enq order: ", potential_enq_order)
    print("Potential deq order: ", potential_deq_order)
    print("All enq order: ", all_enq_orders)
    print("All deq order: ", all_deq_orders)
    print("⚠️ Potential enq order shape", potential_enq_order.shape)
    print("⚠️ Potential deq order shape", potential_deq_order.shape)
    print("⚠️ ALL enq order shape", all_enq_orders.shape)
    print("⚠️ ALL deq order shape", all_deq_orders.shape)
    print("Multiplication: ", cp.vstack(potential_enq_order) @ all_enq_orders )"""
    objective_function = cp.Minimize(cp.sum(cp.abs(cp.vstack(potential_enq_order) @ all_enq_orders - cp.vstack(potential_deq_order) @ all_deq_orders)))
    
    ######### DEFINE AND SOLVE PROBLEM
    problem=cp.Problem(objective_function, constraints=constraints)
    
    problem.solve()
    print("Sub-solution:")
    print("Value: ", problem.value)
    for e in E:
        print("Solution to e:", e.value)
    for d in D:
        print("Solution to d:", d.value)

    ######### CHECK SOLUTION FEASIBILITY
    status = problem.status
    if status in [cp.INFEASIBLE, cp.UNBOUNDED]:
        print("No solution found.")
        return (None, None)

    ######### OUTPUT THE STEP FIRST ORDERS
    decided_enq_ordering = []
    decided_deq_ordering = []
    for i in range(0,min(step,len(inp_list))):
        decided_enq_ordering.append(int(np.dot(E[i].value, all_enq_orders)))
        decided_deq_ordering.append(int(np.dot(D[i].value, all_deq_orders)))

    return (decided_enq_ordering, decided_deq_ordering)
    #return(None,None)

    # För varje potentiell ordering för ett värde, skapa en cp-variabel
    # En svårighet: Skulle behöva skapa en order_array med alla unika orders (kanske sorterade)
    #               Och sedan skapa cp-variabler för alla, och sätta alla constraints för alla som inte finns tillgängliga för en operation till 0
    

do_not_use = {
    1: ([0,1,2,3,4],[0,1,2,3,4,5,6]),       
    2: ([0,1,2,3,4,5],[0,1,2,3,4]),         
    3: ([0,1,2,3,4],[2,3,4,5,6,7,8]),       
    4: ([6,7,8,9,10], [None]),          
    5: ([7,8,9,10,11],[9,10]),              
    6: ([6,7,8,9,10,11],[1,2,3,4,5,6]),     
    7: ([3,4,5,6],[0,1,2,3,4,5,6]),         
    8: ([5,6,7,8],[7,8,9,10]),              
    9: ([0,1,2,3,4,5],[0,1,2,3,4,5,6,7,8]), 
    10: ([6,7,8,9,10],[2,3,4,5,6,7,8,9]),   
    11: ([9,10,11,12], [None]),         
    12: ([7,8,9,10,11],[9,10,11,12]),       
    13: ([12],[8,9,10,11,12])               
}

testdict_with_none = {
    1: ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4, 5, 6]), 
    2: ([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4]), 
    3: ([0, 1, 2, 3, 4], [2, 3, 4, 5, 6, 7, 8]), 
    4: ([6, 7, 8, 9, 10], [4, 5, 6, 7, 8]), 
    5: ([7, 8, 9, 10, 11], [9, 10]), 
    6: ([10, 11], [None]), 
    7: ([3, 4, 5, 6], [0, 1, 2, 3, 4, 5, 6]), 
    8: ([5, 6, 7, 8], [7, 8, 9, 10]), 
    9: ([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5, 6, 7, 8]), 
    10: ([6, 7, 8, 9, 10], [2, 3, 4, 5, 6, 7, 8, 9]), 
    11: ([12], [None]), 
    12: ([7, 8, 9, 10], [4, 5, 6, 7, 8, 9]), 
    13: ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])
}

testdict_no_none = {
    7: ([3,4,5,6],[0,1,2,3,4,5,6]),         # 3 5
    8: ([5,6,7,8],[7,8,9,10]),              # 5 7
    9: ([0,1,2,3,4,5],[0,1,2,3,4,5,6,7,8]), # 4 6
    10: ([6,7,8,9,10],[2,3,4,5,6,7,8,9]),   # 9 8

    11: ([9,10,11,12], [11,12,13]),         # 10 11
    12: ([7,8,9,10,11],[9,10,11,12]),       # 11 12
    13: ([12],[8,9,10,11,12]),               # 12 10
    1: ([0,1,2,3,4],[0,1,2,3,4,5,6]),       # 0 0

    2: ([0,1,2,3,4,5],[0,1,2,3,4]),         # 1 1
    3: ([0,1,2,3,4],[2,3,4,5,6,7,8]),       # 2 2
    4: ([6,7,8,9,10],[4,5,6,7,8]),          # 6 4
    5: ([7,8,9,10,11],[9,10]),              # 7 9       # NOTE: Dequeue blir [] i lösning där man bara tar bort de valda i varje iteration

    6: ([6,7,8,9,10,11],[1,2,3,4,5,6])     # 8 3
}

testdict_small = {
        1: ([0,1], [2,3]),
        2: ([0,1], [2,3]),
        3: ([2,3],[0,1]),
        4: ([2,3],[0,1]),
    }

testdict_no_rank_error = {                    # Har ingen rank error
        1: ([0,1,2], [0,1,2]),
        2: ([0,1,2,3],[0,1,2]),
        3: ([0,1,2,3],[0,1,2,3]),
        4: ([1,2,3],[2,3]),
    }


if __name__=="__main__":
    windowed_linear_programming(testdict_with_none)