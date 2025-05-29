import cvxpy as cp
import numpy as np

# An integer programming solution utilizing ordering representation of intervals
# Each CVXPY variable corresponds to "if an operation is in the potential position"

# NOTE: This integer programming script works for at most ~10 input. And it is not a windowed solution.
# NOTE: There are two known issues. 
#       1)  (Problem occurred when it was implemented as a windowed solution) 
#           Since it simply assigns orders for operations in early subproblems and removes those orders from 
#           later operations, there is a risk that later operations have no available orders to be assigned to.
#
#       2)  It can assign a total order which is not possible to convert to a timeline, 
#           due to operations early in the order having late start timestamps, which may lay 
#           after the end timestamps of oeprations later in the order. 
#           (Think we found a solution to this in the ordering linearization method)

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

# Expects as input: order dict as item:([potential enq orderings], [potential deq orderings])
# Returns: a dict of decided orders as item:(decided enq order, decided deq order)
def integer_linear_programming(inp: dict):

    # Parsing to handle None values
    total_length = len(inp)
    parsed_inp = {}
    count = 0
    for (item, (v1,v2)) in inp.items():
        if None in v2: 
            parsed_inp[item] = (v1,[total_length+count]) # Add order after those actually available. Orders are zero indexed. 
            count += 1
        else: parsed_inp[item] = (v1, v2)

    parsed_inp_list = list(parsed_inp.values())

    enq_order_list = [parsed_inp_list[x][0] for x in range(0, len(parsed_inp_list))]
    deq_order_list = [parsed_inp_list[x][1] for x in range(0, len(parsed_inp_list))]
    nr_enqs = len(enq_order_list)

    # Array with all available potential orders
    # Assumes that the previous parsing to exclude dequeue Nones have been done
    all_enq_orders = np.array([x for x in range(0,len(enq_order_list))])
    all_deq_orders = np.array([x for x in range(0,len(deq_order_list))])

    ######### CREATE CVXPY VARIABLES
    # Enqueue and dequeue variables for each operation value
    # Each CVXPY variable corresponds to "if an operation is in the potential position"
    # There is one CVXPY variable per existing position and operation
    E = []
    D = []
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
    problem.solve(solver=cp.SCIP) # Can set verbose=True for more thorough solver information

    ######### OUTPUT THE SOLUTION
    solution = {}
    for i,k in enumerate(parsed_inp):
        current_enq = int(np.dot(E[i].value, all_enq_orders))
        current_deq = int(np.dot(D[i].value, all_deq_orders))
        if current_deq >= total_length:
            current_deq = None
        solution[k] = (current_enq, current_deq)

    return solution