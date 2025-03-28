import math
import cvxpy as cp
import numpy as np
from timestamp import Timestamp

# A non-integer linear programming script
# Here, CVXPY variables represent enq and deq timestamps
# These are set by CVXPY, when optimizing over an objective function

# Takes as input: timestamp dict
# Returns: the very last end timestamp
def get_last_timestamp(inp: dict):
    last_timestamp = 0
    for (k, v) in inp.items():
        if v.enq_end > last_timestamp: last_timestamp = v.enq_end
        if v.deq_end != None:
            if v.deq_end > last_timestamp: last_timestamp = v.deq_end
    return last_timestamp

# Takes as input: TIMESTAMP dict (of whole problem), span and step
# Returns: two dicts puts and gets, which link keys (operation value) to decided timestamp (linearization point)
def windowed_non_integer_linear_programming(inp: dict, span, step):
    diff = span - step # assumes span >= step

    # Parsing timestamp dict to handle None values (set those timestamps past the last timestamp)
    original_last_timestamp = get_last_timestamp(inp)
    last_timestamp = original_last_timestamp
    for (k,v) in inp.items():
        if v.deq_start is None:
            v.update_deq(last_timestamp+1, last_timestamp+1)
            last_timestamp += 1
            inp[k] = v

    # Main loop:
    start = 0
    total_length = len(inp)
    list_values = list(inp.values())  # List of timestamp objects
    complete_enq_solution = []
    complete_deq_solution = []
    while start < total_length:
        end = start+step
        if(end > total_length): end = total_length
        subset_list_values = [list_values[x] for x in range(start, end)]
        (partial_enq_solution, partial_deq_solution) = non_integer_linear_programming(subset_list_values) # Must maintain order in lists
        complete_enq_solution.extend(partial_enq_solution)
        complete_deq_solution.extend(partial_deq_solution)
        
        start += step # TODO: Få window att fungera

    # Build final output dicts (puts and gets)
    puts = {}
    gets = {}
    for index, key in enumerate(inp):
        if(complete_deq_solution[index] <= original_last_timestamp): # Assumes order has been maintained in lists
            gets[key] = complete_deq_solution[index] # Simply do not include the values that were Dequeue Nones
        puts[key] = complete_enq_solution[index] 

    return (puts, gets)
    
# Takes as input: List of timestamp objects and a string "deq" (or "enq", but does not match against that)
# Returns: The earliest start timestamp and latest end timestamp
def get_total_interval(inp, type):
    # Initial values
    earliest_start = math.inf
    latest_end = 0 

    for timestamp in inp:
        if(type == "deq"):
            start = timestamp.deq_start
            end = timestamp.deq_end
        elif(type == "enq"):
            start = timestamp.enq_start
            end = timestamp.enq_end
        if start < earliest_start: earliest_start = start
        if end > latest_end: latest_end = end
    
    return (earliest_start, latest_end)


# NOTE: Assumes all enqueues have dequeues
# Takes as input: list of timestamp objects (of partial problem)
# Returns: Two lists of decided timestamps (linearization points). For enq/deq respectively.
def non_integer_linear_programming(inp_list):

    ######### CREATE CVXPY VARIABLES
    nr_input = len(inp_list)
    enq_var = []
    deq_var = []
    for i in range(0, nr_input):
        enq_var.extend(cp.Variable(1, integer=False))
        deq_var.extend(cp.Variable(1, integer=False))


    ######### DEFINE CONSTRAINTS
    constraints = []
    for i, timestamp in enumerate(inp_list):
        constraints.append(timestamp.enq_start <= enq_var[i]) # enq_start <= enq_var <= enq_end
        constraints.append(timestamp.enq_end >= enq_var[i])
        constraints.append(timestamp.deq_start <= deq_var[i]) # deq_start <= deq_var <= deq_end
        constraints.append(timestamp.deq_end >= deq_var[i])
        constraints.append(enq_var[i] <= deq_var[i]) 
        # NOTE: There is no constraint ensuring that enq and deq doesn't get the same timestamp (inequalities not allowed)
        #       However, there is a timestamp test that checks these things, and that should be called after calling a linearization method.

    ######### DEFINE OBJECTIVE FUNCTION

    (e_s, e_e) = get_total_interval(inp_list, "enq")
    e_interval_width = e_e - e_s
    (d_s, d_e) = get_total_interval(inp_list, "deq")
    d_interval_width = d_e - d_s
    
    e_rel_pos = np.divide((np.subtract(enq_var, e_s)), e_interval_width) # The position for each enq linearization point within the total interval 
    d_rel_pos = np.divide((np.subtract(deq_var, d_s)), d_interval_width) 
    
    # Optimize to get each enq/deq at a similar position within their respective total interval.
    # There may exist objective functions that give better result.
    objective_function = cp.Minimize(cp.sum(cp.abs(cp.vstack(d_rel_pos) - cp.vstack(e_rel_pos))))
    
    ######### DEFINE AND SOLVE PROBLEM
    problem=cp.Problem(objective_function, constraints=constraints)
    problem.solve(solver=cp.HIGHS ,verbose=True)

    # NOTE: Collects the ROUNDED result in lists. 
    #       Rounding may cause different items to have the same timestamp for either operation.
    #       However, it undo:s floating point calculation problems that otherwise occur.
    decided_enq_timestamp = [round(x.value, 0) for x in enq_var] 
    decided_deq_timestamp = [round(x.value, 0) for x in deq_var]
    
    return (decided_enq_timestamp, decided_deq_timestamp)

test = {
    1: Timestamp(301, 308, 312, 318),
    2: Timestamp(303, 311, 313, 317),
    3: Timestamp(306, 312, 315, 320),
    4: Timestamp(310, 315, 319, 322)
}

if __name__=="__main__":
    windowed_non_integer_linear_programming(test, 13, 13)