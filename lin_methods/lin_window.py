from lin_methods.lin_try import exhaustive_ratio
## psuedo code

'''
run try 25 get linearization points. 

for i in inp-10
    search_lin(inp[i : i+10])

search lin(list)
    start with linearization point from try 25
    from beginning to end do some check to see if it is too early or to late to minimize rank error
    binary search half the search space for the item
    calculate rank error in each step 
    do next one
    return the timestamps when no some threashold for minimization difference is reached 

'''

def lin_window(inp: dict):
    
    temp = exhaustive_ratio(inp)
    temp = dict(sorted(temp.items(), key=lambda x:x[1]))
    for i in range(len(temp)-9):
        for j in temp[i:i+9]:
            vals = inp[j]
        temp[i:i+9] = optimize(vals, temp[i:i+9])


def optimize(inp, tempvect):
    #TODO: beep boop
    print("h")
