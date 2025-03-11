import cvxpy as cp
import numpy as np


# TODO: Consider dequeue None
# TODO: Check that enqueue order is before dequeue order. CONSTRAINT!

def linear_programming():

    """E = np.array([
    [1, 1, 1, 0], # Indices corresponds to possible order positions
    [1, 1, 1, 1],
    [1, 1, 1, 1],
    [0, 1, 1, 1]])

    D = np.array([
    [1, 1, 1, 0],
    [1, 1, 1, 0],
    [1, 1, 1, 1],
    [0, 0, 1, 1]])
    
    enqOrd = [0, 1, 2, 3]
    deqOrd = [0, 1, 2, 3]

    b = np.array([0,0,0,0,0,0,1,2])
    c = np.array([2,2,3,2,3,3,3,3])"""

    #x = cp.Variable(8, integer=True) # each x is 0 or 1 
    x = cp.Variable(4*4*2, integer=True) # First 4*2 values are for enqueue and the rest for dequeue

    #objective_function = (x[0] - x[1]) + (x[2] - x[3]) + (x[4] - x[5]) + (x[6] - x[7])
    objective_function = ((x[0]*1 + x[1]*2 + x[2]*3 + x[3]*4) - (x[16]*1 + x[17]*2 + x[18]*3 + x[19]*4) + 
                          (x[4]*1 + x[5]*2 + x[6]*3 + x[7]*4) - (x[20]*1 + x[21]*2 + x[22]*3 + x[23]*4) +
                          (x[8]*1 + x[9]*2 + x[10]*3 + x[11]*4) - (x[24]*1 + x[25]*2 + x[26]*3 + x[27]*4) +
                          (x[12]*1 + x[13]*2 + x[14]*3 + x[15]*4) - (x[28]*1 + x[29]*2 + x[30]*3 + x[31]*4))

    constraints = [
        x >= 0, x <= 1, #"binary" variables
        x[3] == 0, x[12] == 0, x[19] == 0, x[23] == 0, x[28] == 0, x[29] == 0,   # All x values which are NOT potential orders
        
        # Each enqueue operation must have exactly one of the possible positions
        x[0] + x[1] + x[2] == 1,
        x[4] + x[5] + x[6] + x[7] == 1,
        x[8] + x[9] + x[10] + x[11] == 1,
        x[13] + x[14] + x[15] == 1,
        # Only one of each enqueue operation can take each order position
        x[0] + x[4] + x[8] == 1,
        x[1] + x[5] + x[9] + x[13] == 1,
        x[2] + x[6] + x[10] + x[14] == 1,
        x[7] + x[11] + x[15] == 1,

        # Each dequeue operation must have exactly one of the possible positions
        x[16] + x[17] + x[18] == 1,
        x[20] + x[21] + x[22] == 1,
        x[24] + x[25] + x[26] + x[27] == 1,
        x[30] + x[31] == 1,
        # Only one of each dequeue operation can take each order position
        x[16] + x[20] + x[24] == 1,
        x[17] + x[21] + x[25] == 1,
        x[18] + x[22] + x[26] + x[30] == 1,
        x[27] + x[31] == 1
    ]

    prob=cp.Problem(cp.Minimize(objective_function), constraints=constraints)
    
    prob.solve()

    print("Value: ", prob.value)
    print("Solution to x: ", x.value)


testdict = {
        1: ({0,1,2}, {0,1,2}),
        2: ({0,1,2,3},{0,1,2}),
        3: ({0,1,2,3},{0,1,2,3}),
        4: ({1,2,3},{2,3})
        #5: ({},{None})
    }

def hard_coded_example_with_rank_error():
    x = cp.Variable(4*4*2, integer=True) # First 4*2 values are for enqueue and the rest for dequeue
    #objective_function = (x[0] - x[1]) + (x[2] - x[3]) + (x[4] - x[5]) + (x[6] - x[7])
    objective_function = (cp.abs((x[0]*1 + x[1]*2 + x[2]*3 + x[3]*4) - (x[16]*1 + x[17]*2 + x[18]*3 + x[19]*4)) + 
                        cp.abs((x[4]*1 + x[5]*2 + x[6]*3 + x[7]*4) - (x[20]*1 + x[21]*2 + x[22]*3 + x[23]*4)) +
                        cp.abs((x[8]*1 + x[9]*2 + x[10]*3 + x[11]*4) - (x[24]*1 + x[25]*2 + x[26]*3 + x[27]*4)) +
                        cp.abs((x[12]*1 + x[13]*2 + x[14]*3 + x[15]*4) - (x[28]*1 + x[29]*2 + x[30]*3 + x[31]*4)))
    constraints = [
    x >= 0, x <= 1, #"binary" variables
    x[2] == 0, x[3] == 0, x[6] == 0, x[7] == 0, 
    x[8] == 0, x[9] == 0, x[12] == 0, x[13] == 0,

    x[15] == 0, x[16] == 0, x[19] == 0, x[20] == 0,
    x[25] == 0, x[26] == 0, x[29] == 0, x[30] == 0,

    # Each enqueue operation must have exactly one of the possible positions
    x[0] + x[1] == 1,
    x[4] + x[5] == 1,
    x[10] + x[11] == 1,
    x[14] + x[15] == 1,
    # Only one of each enqueue operation can take each order position
    x[0] + x[4] == 1,
    x[1] + x[5] == 1,
    x[10] + x[14] == 1,
    x[11] + x[15] == 1,

    # Each dequeue operation must have exactly one of the possible positions
    x[17] + x[18] == 1,
    x[21] + x[22] == 1,
    x[23] + x[24] == 1,
    x[27] + x[28] == 1,
    # Only one of each dequeue operation can take each order position
    x[17] + x[21] == 1,
    x[18] + x[22] == 1,
    x[23] + x[27] == 1,
    x[24] + x[28] == 1
    ]
    prob=cp.Problem(cp.Minimize(objective_function), constraints=constraints)

    prob.solve()

    print("💖💖💖💖💖💖")
    print("Value: ", prob.value)
    print("Solution to x: ", x.value)

#linear_programming(testdict)
hard_coded_example_with_rank_error()