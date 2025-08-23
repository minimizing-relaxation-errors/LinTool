# algorithm is based on the idea that if the order of enqueu  and dequeu operations is the same 
# the rank error should be zero. 
# here we create a total ordering of all items which attempts to assign items at the same position in the 
# total ordering as far as possible

import random

def ordering_lin(inp, time_inp):
    ## inp contains full possible positions for enq and deq short and long overlap only contain overlap
    short_overlaps, long_overlaps, split_overlaps, no_deqs = create_overlaps(inp)
    #print(inp)
    """## help print for the structure of the different inputs
    for i in short_overlaps:
        print("short_overlap: ", i, short_overlaps[i], "length: ", len(short_overlaps))
        break
    for i in long_overlaps:
        print("long_overlaps: ", i, long_overlaps[i], "length: ", len(long_overlaps))
        break
    for i in split_overlaps:
        print("split_overlaps: ", i, split_overlaps[i], "length: ", len(split_overlaps))
        break
    for i in no_deqs:
        print("no_deqs: ", i, no_deqs[i], "length: ", len(no_deqs))
        break
    for i in inp:
        print("inp: ", i, inp[i])
        break
    """
    nones = len(no_deqs)
    long_overlaps = dict(sorted(long_overlaps.items(), key=lambda x:len(x[1])))
    nq_index = [0]*len(inp) ## index arrays to keep track of which orders are assigned 0 if not assigned and the key of the dicts otherwise
    dq_index = [0]*(len(inp)-nones)
    potential_per_nqind, potential_per_dqind = pot_per_pos(inp, len(nq_index), len(dq_index))

    ## go through last indices of nq index and assign items with no deq to positions after deq potential orders.
    no_deqs, nq_index = preassign_no_deqs_at_end(no_deqs, nq_index, len(dq_index))
    
    ## assign the ones with one case for having the same enq and deq order to be the same index
    nq_index, dq_index = assign_one_overlap(short_overlaps, nq_index, dq_index)

    split_overlaps, nq_index, dq_index = assign_no_overlap(split_overlaps, nq_index, dq_index, inp)
    
    ## Assign items with several indices overlapping where it is possible to assign both operations to same index
    long_overlaps, nq_index, dq_index = assign_long_overlap(long_overlaps, nq_index, dq_index, inp)
    ## Go through and assign all items that were not possible to put in "optimal" position
    nq_index, dq_index = assign_to_zero(short_overlaps, long_overlaps, no_deqs, nq_index,dq_index, inp, potential_per_nqind, potential_per_dqind)

    # test that no elements are lost in linearization
    test(inp, into_dict(nq_index, dq_index))
    # make linearization into dict for further computation
    order_dict  = into_dict(nq_index, dq_index)
    # Check that all linearization orders are possible with time
    order_dict = check(order_dict, time_inp, inp)
    return order_dict

                    
# assign items with overlap of size 1
def assign_one_overlap(shorts, nq_index, dq_index):
    for item in shorts.items(): 
        if item[1][0] == item[1][1]: ## for the ones with one overlapp 
            item_index = item[1][0]
            if nq_index[item_index] == 0 and dq_index[item_index] == 0:
                nq_index[item_index] = item[0]
                dq_index[item_index] = item[0]
    return nq_index, dq_index

# ensure that the ordering is possible with timestamps
def check(order, time, inp): 
    swaps = 1
    while swaps != 0:
        swaps = 0
        sorted_ordering_dict = {k: v for k, v in sorted(order.items(), key=lambda item: item[1][0])} # Sort on enq_order (ascending)
        keys = list(sorted_ordering_dict.keys())
        for k in range(len(keys)):
            for j in range(k, len(keys)):
                if time[keys[k]].enq_start >= time[keys[j]].enq_end:
                    if order[keys[k]][0] in inp[keys[j]][1] and order[keys[j]][0] in inp[keys[k]][1]:
                        order_swp, order_keep = order[keys[k]][0], order[keys[k]][1]
                        order.update({keys[k]: (order[keys[j]][0], order_keep)})
                        order_keep = order[keys[j]][1]
                        order.update({keys[j]: (order_swp, order_keep)})
                        swaps+=1
                    else:
                        swaps+=1
        no_none = {k:v for k,v in order.items() if v[1] != None}
        sorted_ordering_dict = {k: v for k, v in sorted(no_none.items(), key=lambda item: item[1][1])}
        keys = list(sorted_ordering_dict.keys())
        for k in range(len(keys)):
            for j in range(k, len(keys)):
                if time[keys[k]].deq_start >= time[keys[j]].deq_end:
                    if order[keys[k]][1] in inp[keys[j]][2] and order[keys[j]][1] in inp[keys[k]][2]:
                        order_swp, order_keep = order[keys[k]][1], order[keys[k]][0]
                        order.update({keys[k]: (order_keep, order[keys[j]][1])})
                        order_keep = order[keys[j]][0]
                        order.update({keys[j]: (order_keep, order_swp)})
                        swaps+=1
                    else:
                        swaps+=1
    return order

# assign items with no overlap (split) to available positions
def assign_no_overlap(split_overlaps, nq_index, dq_index, inp):
    keys = list(split_overlaps) ## only contains split items at this point
    for i in keys: 
        curr_item = split_overlaps[i]
        if nq_index[curr_item[0]] == 0 and dq_index[curr_item[1]] == 0: ## try to minimize distance in split items by chosing closest items
            nq_index[curr_item[0]] = i
            dq_index[curr_item[1]] = i
            continue

        else: 
            #neither was available 
            # sort options by closest items
            # try and assign in order
            found_deq = 0
            found_enq = 0
            enq_opts = inp[i][1]
            deq_opts = inp[i][2]
            if enq_opts[-1] == curr_item[0]:
                enq_opts.reverse()
            if deq_opts[-1] == curr_item[1]:
                deq_opts.reverse()
            for j in range(max(len(enq_opts), len(deq_opts))):
                if found_enq == 0:
                    if not j  >= len(enq_opts)-1:
                        e = enq_opts[j]
                        if nq_index[e] == 0:
                            nq_index[e] = i
                            found_enq = e        
                if found_deq == 0:
                    if not j >= len(deq_opts)-1:
                        d = deq_opts[j]
                        if dq_index[d] == 0:
                            dq_index[d] = i
                            found_deq = d
                if found_deq != 0 and found_enq != 0:
                    split_overlaps.pop(i)
                    break
    return split_overlaps, nq_index, dq_index

# remake long overlap dict to structure of split overlaps
def splitting_longs(longs, nq_index, dq_index, inp):
    longys = dict()
    keys = longs.keys()
    #print(longs)
    for k in keys:
        longys.update({k: (longs[k][0], longs[k][0])})
    return longys, nq_index, dq_index
    
## assigns items with overlapping potential orders > 1
def assign_long_overlap(longs, nq_index, dq_index, inp):
    keys = list(longs.keys())
    for k in keys:
        is_set = False
        for i in longs[k]:
            if nq_index[i] == 0 and dq_index[i] == 0:
                nq_index[i] = k
                dq_index[i] = k
                longs.pop(k)
                set = True
                break
            else:
                pass
    longss, nq_index, dq_index = splitting_longs(longs, nq_index, dq_index, inp)
    longss, nq_index, dq_index = assign_no_overlap(longss, nq_index, dq_index, inp)
    long = dict()
    for l in longss:
        long.update({l: longs[l]})

    return(long, nq_index, dq_index)

# create datastructures used in the algorithms from input
def create_overlaps(inp):
    for i in inp.keys():
        (enqs, deqs) = inp[i]
        overlap = ()
        for e in enqs:
            for d in deqs:
                if e == d:
                    overlap = overlap + tuple([e]) # add all overlapping timestamps to a tuple 
                #else: pass
        if overlap == (): # if there are no overlapping
            min = 100000
            for e in enqs:
                for d in deqs:
                    if d != None:
                        if abs(int(e)-int(d)) < min:
                            min = abs(e-d)
                            overlap = (e,d) # if there is a deq, choose the ones that are closest (first, last) or (last, first) usually
                    else: 
                        overlap = tuple(enqs) +(None,) # if there is no deq, the "overlapp" is just all enq positions, adding none to the end for easy identification in assignment step

        inp.update({i:(overlap, enqs, deqs)}) # return 
    sort = dict(sorted(inp.items(), key=lambda x:len(x[1][0])))
    short_overlaps = dict() ## no overlapp (two values), or one overlapp
    long_overlaps = dict()
    nones = dict() # items with no dequeue
    split_overlap = dict()
    num = 0
    for value in sort.keys():
        (pos, enqs, deqs) = sort[value]
        if len(pos) == 1:
            short_overlaps.update({value: (pos[0],pos[0])}) # add so that all tuples have length 2 (for enq, deq). 
        elif None in pos:
            print(pos)
            nones.update({value: pos})
        elif len(pos) == 2:
            if abs(pos[0] - pos[1]) != -1:
                split_overlap.update({value: (pos[0], pos[1])}) # add the closest pair ones. to the 
        elif len(pos) > 2:
            long_overlaps.update({value: pos})
        else: 
            print(value, pos, "\n", inp[value])
            num+=1
            print(num)
    return short_overlaps, long_overlaps, split_overlap, nones

# loops through indices at the end of nq where there is no corresponding dq
#  and tries to assign items that have no dequeue operation
def preassign_no_deqs_at_end(no_deqs, nq_index, dq_index_len): 
    for n in range(dq_index_len, len(nq_index)):
        for item in no_deqs.items():
            if n in item[1] and nq_index[n] == 0:
                print("preass:", item)
                nq_index[n] = item[0]
                no_deqs.pop(item[0])
                break
    return no_deqs, nq_index

# go through all indices that are still 0 in dq and nq index
# assigns one potential value, disregarding where the corresponding operation is
# lastly goes through and assigns to unassigned orders where there are no options by
# assigning one of the potential values at random, and then removing it from its already assigned position
def assign_to_zero(shorts, longs, no_deq, nq_index, dq_index, inp, pot_per_nq, pot_per_dq):
    keys = list(shorts.keys()) + list(longs.keys()) + list(no_deq.keys()) 
    potentials = []
    for e in range(len(nq_index)):
        could_fits = []
        if nq_index[e] == 0:
            could_fits = [e]
            for k in keys:
                if e in inp[k][1]:
                    could_fits.append(k)
        potentials.append(could_fits)
    potentials.sort(key=len)
    no_pots = []
    for p in potentials:
        if len(p) == 1:
            no_pots.append(p[0])
        if len(p) > 1:
            min = 100000
            item = None
            
            for i in p[1:]:
                if len(inp[i][1]) < min:
                    min = len(inp[i][1])
                    item = i
            if not item in nq_index: ## this is true if item is None
                print(item, "assign rest ❌❌❌")
                nq_index[p[0]] = item 
            if item != None:
                keys.remove(item)
            # go through and assign one of them removing the potential from all other lists in the datastructure         
            for q in range(len(potentials)):
                if item in potentials[q]:
                    potentials[q].remove(item)
    potentials = []
    for d in range(len(dq_index)):
        could_fits = []
        if dq_index[d] == 0:
            could_fits = [d]
            for k in keys:
                if d in inp[k][2]:
                    could_fits.append(k)
        potentials.append(could_fits)
    potentials.sort(key=len)
    no_pots = []
    for p in potentials:
        if len(p) == 1:
            no_pots.append(p[0])
        if len(p) > 1:
            min = 1000
            item = None
            for i in p[1:]:
                if len(inp[i][2]) < min:
                    min = len(inp[i][2])
                    item = i
            if not item in dq_index and item != None: ## true if item is None 
                dq_index[p[0]] = item
            if item != None:
                keys.remove(item)
            for q in range(len(potentials)):
                if item in potentials[q]:
                    potentials[q].remove(item)
    while not (nq_index.count(0) == 0 and dq_index.count(0) == 0):
        for n in range(len(nq_index)):
            if nq_index[n] == 0:
                poss = pot_per_nq[n]
                ass = False
                for p in poss:
                    if p not in nq_index:
                        nq_index[n] = p
                        if p == None:
                            print(p, "assign to zero p🤏🤏🤏")
                        ass = True
                        break
                if not ass:
                    item = random.choice(poss)
                    ind = nq_index.index(item)
                    nq_index[ind] = 0 
                    nq_index[n] = item
        for d in range(len(dq_index)):
            if dq_index[d] == 0:
                poss = pot_per_dq[d]
                ass = False
                for p in poss:
                    if p not in dq_index:
                        dq_index[d] = p
                        ass = True
                        break
                if not ass:
                    item = random.choice(poss)
                    ind = dq_index.index(item)
                    dq_index[ind] = 0 
                    dq_index[d] = item
    return nq_index, dq_index

# create lists of lists where the list at a certain index 
# corresponds to all of the items that could go in that index in the ordering
def pot_per_pos(inp, num_nq, num_dq): 
    nq = []
    for i in range(num_nq+1):
        nq.append([])
    dq = []
    for i in range(num_dq+1):
        dq.append([])
    for k in inp.keys():
        for n in inp[k][1]:
            nq[n].append(k)
        for d in inp[k][2]:
            if d != None:
                #print(inp[k])
                #print(num_dq)
                dq[d].append(k)
            else: pass
    return nq, dq

# nq_index and dq_index into shape of dictionary required from "get timestamp from order" function.
def into_dict(nq_index, dq_index): 
    dic = dict()
    if None in nq_index:
        print("nq")
    if None in dq_index:
        print("dq: ")
    for n in range(len(nq_index)):
        for d in range(len(dq_index)):
            if nq_index[n] == dq_index[d]:
                dic.update({nq_index[n]: (n, d)})
        if nq_index[n] not in dic.keys():
            dic.update({nq_index[n]: (n, None)})
    if None in dic.keys():
        print(dic[None])
    return dic

# test that the output size is the same as the input size 
def test(inp, dic):
    for d in dic.keys():
        #print(d)
        if not dic[d][0] in inp[d][1]:
            print("nq: ",d, ": ",dic[d], inp[d])
        if not dic[d][1] in inp[d][2]:
            print("dq: ",d, ": ", dic[d], inp[d])
    if not len(inp) == len(dic):
        print("wrong size, elements lost")

