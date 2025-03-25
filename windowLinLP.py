import cvxpy as cp
import numpy as np
from computeRankError import compute_rank_error
from linTry import exhaustive_ratio
from timestamp import Timestamp

# TODO: Följande är fortfarande existerande problem:
#       - Fastställa hur stort problem som kan köras utan Window-funktionaliteten.
#       - Fastställa att det fungerar med dequeue None-värden.
#       - Window-lösningen fungerar ej.
# TODO: Fixa sista TODOs, e.g. tester.
# TODO: Skriv dokumentation (i koden och för thesis)

''' Fastställa hur stort problem som kan köras utan Window-funktionaliteten:
Resultat än så länge: 200-faaaq fungerar och tar nog ca 10-15 min på laptop.
TODO: Undersöka hur stort som går att köra och hur lång tid de olika storlekarna tar. Börja på odysseus men gå över till ithaca.
TODO: Undersök om någon annan solver kan användas som kan hantera större problem.
'''

''' Fastställa att det fungerar med dequeue None-värden:
Resultat än så länge: Fungerar på delar av större filer med None (stoppas pga ej fungerande Window). Fungerar även på väldigt små test dictionaries.
TODO: Skapa mindre filer och lägg manuellt in Nonevärden som sållats ut. Alt. ändra create_short_file så att den lägger tillbaka None-värden. Testa sedan på dessa filer.
'''

''' Window-lösningen fungerar ej:
Resultat än så länge: Fungerar tills någon senare operation får slut på potential orderings.
TODO: Testa olika metoder, t.ex. att sortera på antal potential orders (stigande) och bestäm de med få potentilla,
      eller att använda overlap (antal lika orders mellan enq och deq för ett visst värde)
      eller ta fram antal occurances för varje potentiell ordering och gå efter den (typ samma som tidigare punkter)
TODO: Försök komma på metoder som faktiskt kan garantera lösning.
'''


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


# Expects ordering dict (of total problem), span and step
def windowed_linear_programming(inp: dict, span, step):
    diff = span - step # must be positive probably

    # Parsing to handle None values
    total_length = len(inp)
    parsed_inp = {}
    count = 0
    for (key, (v1,v2)) in inp.items():
        if None in v2: 
            parsed_inp[key] = (v1,[total_length+count]) # Add order after those actually available to the other dequeues. Orders are zero indexed. 
            count += 1
        else: parsed_inp[key] = (v1, v2)

    start = 0
    list_values = list(parsed_inp.values())
    complete_enq_ordering = []
    complete_deq_ordering = []
    while start < total_length:
        end = start+span
        if(end > total_length): end = total_length                          # TODO: This is a bit funky. Perhaps it should simply optimize over the >= span final items. Since the last span otherwise just shrinks and does the optimization maybe uneccessarily at the end
        subset_list_values = [list_values[x] for x in range(start, end)]
        (decided_enq_ordering, decided_deq_ordering) = linear_programming(subset_list_values, span, step, diff) # Decides the step first elements orderings

        # Remove the decided on orderings from the rest of the dict elements
        # TODO (Window lösning fungerar ej): Får ibland NoneType-problem för att den tommer någon senare parsed_inp.item helt och när den då försöker iterera v2 blir det fel.
        for (key, (v1,v2)) in parsed_inp.items():
            for item in decided_enq_ordering:
                if item in v1: parsed_inp[key] = (v1.remove(item), v2)
            for item in decided_deq_ordering:
                if item in v2: parsed_inp[key] = (v1, v2.remove(item))
        
        # Append partial ordering to complete ordering
        complete_enq_ordering.extend(decided_enq_ordering)  # TODO: Can probably just build solution dict right here and remove this code
        complete_deq_ordering.extend(decided_deq_ordering)

        start += step

    # Build final output dict
    solution = {}
    for index, key in enumerate(parsed_inp):
        if(complete_deq_ordering[index] >= total_length): solution[key] = (complete_enq_ordering[index], None)
        else: solution[key] = (complete_enq_ordering[index], complete_deq_ordering[index])

    test_if_valid(parsed_inp, solution)

    return solution

# Expects an array A with n rows and m columns, outputs an array A with m rows and n columns
# Expects rows in A to be cvxpy-variables
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
# Expects ordering dict (of partial problem)
def linear_programming(inp_list, span, step, diff):
    enq_order_list = [inp_list[x][0] for x in range(0, len(inp_list))]
    deq_order_list = [inp_list[x][1] for x in range(0, len(inp_list))]
    nr_enqs = len(enq_order_list)

    # Create sets to flatten the lists of lists into one set, which excludes duplicates
    enq_order_set = set()
    deq_order_set = set()
    for i in range(0, nr_enqs):
        enq_order_set.update(enq_order_list[i])
        deq_order_set.update(deq_order_list[i])

    # Array with potential orders (sorted, no duplicates)
    all_enq_orders = np.array(sorted(list(enq_order_set)))   # Detta är ganska cursed
    all_deq_orders = np.array(sorted(list(deq_order_set)))

    ######### CREATE CVXPY VARIABLES
    E = []
    D = []
    # Enqueue and dequeue variables for each operation value
    # As many CVXPY variables as there are potential positions for each operation
    for i in range(0, nr_enqs):            
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
        this_deq_orders = deq_order_list[i]

        # Compare current operation value's enq/deq to all potential enq/deq orderings
        # If current operation value does not have any of them, set constraint that the corresponding CVXPY variable must be 0 (cannot be chosen)
        for j in range(0, len(all_enq_orders)):
            if(all_enq_orders[j] not in this_enq_orders):
                constraints.append(E[i][j] == 0)
        for j in range(0,len(all_deq_orders)):
            if (all_deq_orders[j] not in this_deq_orders):
                constraints.append(D[i][j] == 0)
        
        # Each operation must have exactly one order
        constraints.append(cp.sum(E[i]) == 1) 
        constraints.append(cp.sum(D[i]) == 1)

    # Each order can only be "occupied" by at most one operation (can be more possible orders than operations)
    transposed_E = transpose(E)
    transposed_D = transpose(D)
    for i in range(0, len(all_enq_orders)):
        constraints.append(cp.sum(transposed_E[i]) <= 1) 
    for i in range(0,len(all_deq_orders)):
        constraints.append(cp.sum(transposed_D[i]) <= 1)

    ######### DEFINE OBJECTIVE FUNCTION
    potential_enq_order = np.array(E)
    potential_deq_order = np.array(D)
    objective_function = cp.Minimize(cp.sum(cp.abs(cp.vstack(potential_enq_order) @ all_enq_orders - cp.vstack(potential_deq_order) @ all_deq_orders)))
    
    ######### DEFINE AND SOLVE PROBLEM
    problem=cp.Problem(objective_function, constraints=constraints)
    
    problem.solve()
    '''print("Sub-solution:")
    print("Value: ", problem.value)
    for e in E:
        print("Solution to e:", e.value)
    for d in D:
        print("Solution to d:", d.value)'''

    ######### CHECK SOLUTION FEASIBILITY
    # TODO: DO this some other time, and make sure to catch the return in the other function when it calls this one
    #status = problem.status
    #if status in [cp.INFEASIBLE, cp.UNBOUNDED]:
    #    print("No solution found.")
    #    return (None, None)

    ######### OUTPUT THE STEP FIRST DECIDED ORDERS
    decided_enq_ordering = []
    decided_deq_ordering = []
    for i in range(0,min(step,len(inp_list))):
        decided_enq_ordering.append(int(np.dot(E[i].value, all_enq_orders)))
        decided_deq_ordering.append(int(np.dot(D[i].value, all_deq_orders)))

    return (decided_enq_ordering, decided_deq_ordering)

"""if __name__=="__main__":
    windowed_linear_programming(testdict)"""