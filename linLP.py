import cvxpy as cp
import numpy as np

# NOTE: This solution is pretty useless for high number of operations. This is just a step in the development.


# NOTE DEQ INF

# TODO: Needs to translate the ordering into a timestamp dictionary again

# Creates two arrays of cvxpy variable arrays, one for enqueue operations and one for dequeue operations
# Each variable array corresponds a single enq/deq operation
# Each variable corresponds to a potential order of the enq/deq operation
# Only one variable per operation can be set to 1, the rest must be 0. This is regulated in the constraints in linear_programming().
#  E = np.array([
#    [x11, x12, x13, x14], # Indices corresponds to possible order positions for first operation
#    [x21, x22, x23, x24],
#    [x31, x32, x33, x34],
#    [x41, x42, x43, x44]])
# n x n matrices, where n is the number of values (i.e. number of enq operations). For both enq/deq matrices.
# I.e. big ass matrices. That CVXPY probably will not like later when we run for large n.
def get_variable_matrix(inp:dict, n):
    E = []
    D = []
    for i in range(0,n):
        # TODO: Want to NOT APPEND when tuple[1] contains None. However, that will mess with the order in objective function. This current solution simply cannot handle deq None.            
        E.append(cp.Variable(n, integer=True))
    for i in range(0,n):     
        D.append(cp.Variable(n, integer=True))
    return (E, D)

def get_objective_function(E, D, n):
    order_vector = np.array(range(1, n+1))
    potential_enq_order = np.array(E)
    potential_deq_order = np.array(D)
    return cp.Minimize(cp.sum(cp.abs(potential_enq_order @ order_vector - potential_deq_order @ order_vector)))

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

def get_constraints(inp:dict, E, D, n):
    # when creating constraints, set corresponding variable to 0 if it does not exist in order_list, 
    # and do "sum rest of the variables = 1"
    constraints = []
    for i, tuple in enumerate(inp.values()):
        constraints.append(E[i] >= 0) # Binary variables
        constraints.append(E[i] <= 1)
        constraints.append(D[i] >= 0)
        constraints.append(D[i] <= 1)

        enq_order_list = tuple[0] # Potential orderings for this particular value's enqueue
        deq_order_list = tuple[1]

        # If value does not have order j as a potential enq/deq order, set corresponding variable to 0 as constraint
        for j in range(0, n): 
            if(j not in enq_order_list): 
                constraints.append(E[i][j] == 0)
            if (j not in deq_order_list): 
                constraints.append(D[i][j] == 0)

        constraints.append(cp.sum(E[i]) == 1) # Each operation can only have a single order
        constraints.append(cp.sum(D[i]) == 1) 

    transposed_E = transpose(E)
    transposed_D = transpose(D)

    for i in range(0, n):
        constraints.append(cp.sum(transposed_E[i]) == 1) # Each order can only be "occupied" by a single operation
        constraints.append(cp.sum(transposed_D[i]) == 1)
    
    return constraints

def linear_programming(inp:dict):
    n = len(inp)
    (E, D) = get_variable_matrix(inp, n)

    problem=cp.Problem(get_objective_function(E, D, n), constraints=get_constraints(inp, E, D, n))
    
    problem.solve()
    print("Value: ", problem.value)
    for e in E:
        print("Solution to e:", e.value)
    for d in D:
        print("Solution to d:", d.value)


testdict_no_rank_error = {                    # Har ingen rank error
        1: ([0,1,2], [0,1,2]),
        2: ([0,1,2,3],[0,1,2]),
        3: ([0,1,2,3],[0,1,2,3]),
        4: ([1,2,3],[2,3]),
    }

testdict_has_rank_error = {                    # Har min rank error 4. Motsvarar dock ej value.
        1: ([0,1], [2,3]),
        2: ([0,1], [2,3]),
        3: ([2,3],[0,1]),
        4: ([2,3],[0,1]),
    }

testdict_no_none = {
    1: ([0,1,2,3,4],[0,1,2,3,4,5,6]),       # 0 0
    2: ([0,1,2,3,4,5],[0,1,2,3,4]),         # 1 1
    3: ([0,1,2,3,4],[2,3,4,5,6,7,8]),       # 2 2
    4: ([6,7,8,9,10],[4,5,6,7,8]),          # 6 4
    5: ([7,8,9,10,11],[9,10]),              # 7 9
    6: ([6,7,8,9,10,11],[1,2,3,4,5,6]),     # 8 3
    7: ([3,4,5,6],[0,1,2,3,4,5,6]),         # 3 5
    8: ([5,6,7,8],[7,8,9,10]),              # 5 7
    9: ([0,1,2,3,4,5],[0,1,2,3,4,5,6,7,8]), # 4 6
    10: ([6,7,8,9,10],[2,3,4,5,6,7,8,9]),   # 9 8
    11: ([9,10,11,12], [11,12,13]),         # 10 11
    12: ([7,8,9,10,11],[9,10,11,12]),       # 11 12
    13: ([12],[8,9,10,11,12])               # 12 10
}

testdict_with_none = {
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

if __name__=="__main__":
    linear_programming(testdict_no_none)