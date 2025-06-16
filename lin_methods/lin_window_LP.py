import math
import cvxpy as cp
import numpy as np

# A linear programming script
# Here, CVXPY variables represent enq and deq timestamps respectively
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

# This is the main function to be called from other files when running this linearization method
# Takes as input: timestamp dict (of whole problem), size of the window (size of subproblem in number of items)
# Returns: two dicts puts {item: enq_point} and gets {item: deq_point}
def windowed_linear_programming(inp: dict, size):

    original_last_timestamp = get_last_timestamp(inp)
    original_first_timestamp = math.inf
    for ts in inp.values():
        e_s = ts.enq_start
        if e_s < original_first_timestamp: original_first_timestamp = e_s

    ### Pre-processing
    short_timestamps = {}
    for (k,v) in inp.items():
        e_start = v.enq_start - original_first_timestamp # Shorten all timestamps (should still be integer)
        e_end = v.enq_end - original_first_timestamp
        if v.deq_start is None: # Handling None values (set those timestamps past the last timestamp)
            d_start = (original_last_timestamp + 1) - original_first_timestamp
            d_end = (original_last_timestamp + 1) - original_first_timestamp
        else:
            d_start = v.deq_start - original_first_timestamp
            d_end = v.deq_end - original_first_timestamp
        short_timestamps[k] = (e_start, e_end, d_start, d_end)
    
    ''' last_timestamp = original_last_timestamp
    for (k,v) in inp.items():
        if v.deq_start is None:
            v.update_deq(last_timestamp+1, last_timestamp+1)
            last_timestamp += 1
            inp[k] = v'''

    # Main loop:
    start = 0
    total_length = len(inp)
    list_values = list(short_timestamps.values())  # List of timestamps
    complete_enq_solution = []
    complete_deq_solution = []
    out_str = ""
    while start < total_length:
        end = start+size
        if(end > total_length): end = total_length
        subset_list_values = [list_values[x] for x in range(start, end)]
        (partial_enq_solution, partial_deq_solution, is_feasible, is_bounded, is_optimal, tmp_out_str) = linear_programming(subset_list_values) # Must maintain order in lists
        complete_enq_solution.extend([x + original_first_timestamp for x in partial_enq_solution])
        complete_deq_solution.extend([x + original_first_timestamp for x in partial_deq_solution])

        if not is_optimal:
            out_str += "Solution interval [" + str(start) + ", " + str(end) + "] is NOT OPTIMAL"
        if not is_feasible:
            out_str += "Solution interval [" + str(start) + ", " + str(end) + "] is INFEASIBLE"
        if not is_bounded:
            out_str += "Solution interval [" + str(start) + ", " + str(end) + "] is UNBOUNDED"

        out_str += tmp_out_str
        
        start = end

    # Build final output dicts (puts and gets)
    puts = {}
    gets = {}
    for index, key in enumerate(inp):
        if(complete_deq_solution[index] <= original_last_timestamp): # Assumes order has been maintained in lists
            gets[key] = complete_deq_solution[index] # Only include dequeues that were NOT deuque none
        puts[key] = complete_enq_solution[index] 

    #sorted_enq_sol = sorted(complete_enq_solution)
    #sorted_deq_sol = sorted(complete_deq_solution)
    # out_str += str(sorted_enq_sol) + "\n" + str(sorted_deq_sol) + "\n"

    return (puts, gets, out_str)
    
# Takes as input: List of timestamp objects and a string "deq" or "enq"
# Returns: The earliest start timestamp and latest end timestamp
def get_total_interval(inp, type):
    # Initial values
    earliest_start = math.inf
    latest_end = 0 

    for (e_start, e_end, d_start, d_end) in inp:
        if(type == "deq"):
            start = d_start
            end = d_end
        elif(type == "enq"):
            start = e_start
            end = e_end
        if start < earliest_start: earliest_start = start
        if end > latest_end: latest_end = end
    
    return (earliest_start, latest_end)

# A linear programming function
# NOTE: Assumes all enqueues have dequeues
# Takes as input: list of timestamp objects (of partial problem)
# Returns: Two lists of decided timestamps (linearization points). For enq/deq respectively.
def linear_programming(inp_list):

    ######### CREATE CVXPY VARIABLES
    nr_input = len(inp_list)
    enq_var = []
    deq_var = []
    for i in range(0, nr_input):
        enq_var.extend(cp.Variable(1, integer=False))
        deq_var.extend(cp.Variable(1, integer=False))

    ######### DEFINE CONSTRAINTS
    constraints = []
    for i, (e_start, e_end, d_start, d_end) in enumerate(inp_list):
        constraints.append(e_start <= enq_var[i]) # enq_start <= enq_var <= enq_end
        constraints.append(e_end >= enq_var[i])
        constraints.append(d_start <= deq_var[i]) # deq_start <= deq_var <= deq_end
        constraints.append(d_end >= deq_var[i])
        constraints.append(enq_var[i] <= deq_var[i]) 
        # NOTE: There is no constraint ensuring that enq and deq doesn't get the same timestamp (equalities not allowed)
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
    problem.solve(solver=cp.HIGHS)

    is_feasible = problem.status != "infeasible"
    is_bounded = problem.status != "unbounded"
    is_optimal = problem.status == "optimal"

    if problem.status == "infeasible":
        print("Problem status: ", problem.status)
 
    out_str = ""

    for constr in problem.constraints:
        residual = constr.violation()
        if np.max(np.abs(residual)) > 0:
            out_str += "Constraint violation is: " + str(np.max(np.abs(residual))) + "\n"

    # NOTE: Collects the ROUNDED result in lists. 
    #       Rounding may cause different items to have the same timestamp for either operation.
    #       However, it undo:s floating point calculation problems that otherwise occur.
    decided_enq_timestamp = [x.value for x in enq_var] 
    decided_deq_timestamp = [x.value for x in deq_var]
    
    #decided_enq_timestamp = [x.value for x in enq_var] 
    #decided_deq_timestamp = [x.value for x in deq_var]

    for i, (e_start, e_end, d_start, d_end) in enumerate(inp_list):
        if(enq_var[i].value < e_start or enq_var[i].value > e_end):
            out_str += str(e_start) + " < " + str(round(enq_var[i].value,0)) + " < " + str(e_end) + "\n"
        if(deq_var[i].value < d_start or deq_var[i].value > d_end):
            out_str += str(d_start) + " < " + str(round(deq_var[i].value, 0)) + " < " + str(d_end) + "\n"

    return (decided_enq_timestamp, decided_deq_timestamp, is_feasible, is_bounded, is_optimal, out_str)