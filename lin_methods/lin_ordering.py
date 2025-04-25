from utils.un_pickle import un_pickle

def ordering_lin(inp, filename):
    #inp = dict()
    #inp = un_pickle(filename)
    ## do a first pass to see "good positions" are just the enq possible positions due to no deq for the item
    short_overlaps, long_overlaps, split_overlaps, no_deqs = create_overlaps(inp)
    for i in short_overlaps:
        print("short_overlap: ", i, short_overlaps[i])
        break
    for i in long_overlaps:
        print("long_overlaps: ", i, long_overlaps[i])
        break
    for i in split_overlaps:
        print("split_overlaps: ", i, split_overlaps[i])
        break
    for i in no_deqs:
        print("no_deqs: ", i, no_deqs[i])
        break
    for i in inp:
        print("inp: ", i, inp[i])
        break
    nones = len(no_deqs)
    ## above here should work as intended
    #print(inp)
    long_overlaps = dict(sorted(long_overlaps.items(), key=lambda x:len(x[1])))
    nq_index = [0]*len(inp) ## index arrays to keep track of which orders are assigned 0 if not assigned and the key of the dicts otherwise
    dq_index = [0]*(len(inp)-nones)
    set_orders = dict()
    half_set_orders = dict()
    non_assigned = dict()
    #print(short_overlap)
    ## inp contains full possible positions for enq and deq short and long overlap only contain overlap
    set_orders, nq_index, dq_index = assign_one_overlap(short_overlaps, set_orders, nq_index, dq_index)
    ## go through long overlap and set enq with none as deq that can be in position of after all deqs.

    no_deqs, half_set_orders, nq_index, dq_index = preassign_no_deqs_at_end(no_deqs, half_set_orders, nq_index, dq_index)
    #print(half_set_orders)
    ## add the split elements so we can take care of them after
    split_overlaps, half_set_orders, nq_index, dq_index, inp = assign_no_overlap(split_overlaps, half_set_orders, nq_index, dq_index, inp)

    for j in range(len(nq_index)):
        if nq_index[j] == 0 and dq_index[j] == 0:
            # go through and assign from long overlap where last element is not none
            keys = list(long_overlaps)
            for o in keys:
                if j in long_overlaps[o] :
                    nq_index[j] = o
                    dq_index[j] = o
                    move = long_overlaps.pop(o)
                    #print(move)
                    half_set_orders.update({o: (j,j)})
                    #print(half_set_orders)
                    break
            if nq_index == 0 and dq_index == 0:
                tmp = dict()
                # loop over keys from half assigned in inp where j is in good poss, add to non_assigned. 
                keys = list(half_set_orders)
                for k in keys:
                    if j in inp[k][0]:
                        tmp.update({k: inp[k][0]})
                    else: continue
                tmp = dict(sorted(tmp.items(), key=lambda x:len(x[1])))
                # tmp now contains items that have previously assigned orders sorted by the length of available positions for 
                # next we assign the first option in this list to the position j and set the previously choosen order 
                nd = tuple()
                for t in tmp.keys():
                    half_set_orders.pop(t)
                    half_set_orders.update({t: (j,j)})
                    for n in range(len(nq_index)):
                        if nq_index[n] == t:
                            nq_index[n] == 0
                            nd = nd + (n,)
                            break
                    for d in range(len(dq_index)):
                        if dq_index[d] == t:
                            dq_index[d] = 0
                            nd = nd + (d,)
                            break
                    break
                if nd[0] == nd[1]:
                    #handle reassignment of nq_[n] and dq[d]  
                    print("you reached the unholy place where you need to do functional decomposition" )
                    raise RuntimeError                  
        else: continue
    ## time for "good" assignment of the indices where it is not possible to assign the same value to the nq and dq order (because we tried to minimize the split ones first)
    # TODO: change to loop over long overlaps. 
    for n in range(len(nq_index)):
        if nq_index[n] == 0:
            go_on = True
            for d in range(100): 
                if (n-d) >= 0 and (n + d) < len(dq_index):
                    if dq_index[n-d] == 0:
                        #check if there is a value that can be assigned to both n and d that does not contain none
                        go_on = False
                        break
                    elif dq_index[n+d] == 0:
                        #check if there is an item that can be assigned to both n and d that does not contain None
                        go_on = False
                        break
            if go_on: ## there was no value for 
                if n in (no_deqs.values()):
                    # assign some element with none 
                    break
                else: 
                    #start looking for options in half set 
                    break
                    

def assign_one_overlap(shorts, sets, nq_index, dq_index):# -> {sets, non_assigned, nq_index, dq_index}:# DONE?
    for item in shorts.items(): 
        #print(item)
        if item[1][0] == item[1][1]: ## for the ones with one overlapp 
            item_index = item[1][0]
            if nq_index[item_index] == 0 and dq_index[item_index] == 0:
                nq_index[item_index] = item[0]
                dq_index[item_index] = item[0]
                #move = short_overlap.pop(item[0])
                sets.update({item})
    return sets, nq_index, dq_index

def assign_no_overlap(split_overlaps, half_set_orders, nq_index, dq_index, inp):# -> {no_overlap, nq_index, dq_index}:
    keys = list(split_overlaps) ## only contains split items at this point
    for i in keys: 
        curr_item = split_overlaps[i]
        if nq_index[curr_item[0]] == 0 and dq_index[curr_item[1]] == 0: ## try to minimize distance in split items by chosing previous minimal
            nq_index[curr_item[0]] = i
            dq_index[curr_item[1]] = i
            move = split_overlaps.pop(i)
            half_set_orders.update({i: move})
            break
            #print(half_set_orders)
        elif nq_index[curr_item[0]] == 0: ## nq order was available but not dq
            nq_index[curr_item[0]] = i
            #print(inp[i][2])
            deq_opts = inp[i][2]
            if deq_opts[-1] == curr_item[1]:
                deq_opts.reverse()
            for d in deq_opts:
                if dq_index[d] == 0:
                    dq_index[d] == i
                    half_set_orders.update({i: (curr_item[0], d)})
                    split_overlaps.pop(i)
                    break
                else: continue
        elif dq_index[curr_item[1]] == 0: ## dq order was avaliable but not nq
            dq_index[curr_item[1]] = i
            enq_opts = inp[i][1]
            if enq_opts[-1] == curr_item[0]:
                enq_opts.reverse()
            for e in enq_opts:
                if nq_index[e] == 0:
                    nq_index[e] = i
                    half_set_orders.update({i: (e, curr_item[1])})
                    split_overlaps.pop(i)
                    break
                else: continue
        else: #neither was available 
            # vet vilka ändar som är närmast
            # skapa set variabel för enq och deq
            # skapa enq och deq opts och eventuellt reversa dem så att närmsta ändarna är först
            # range loop på den längre av dem 
            # if not set check if enq[j] and deq[j] is available 
            # when both are set put in half set items and remove from non_assigned.
            found_deq = 0
            found_enq = 0
            enq_opts = inp[i][1]
            deq_opts = inp[i][2]
            if enq_opts[-1] == curr_item[0]:
                enq_opts.reverse()
            if deq_opts[-1] == curr_item[1]:
                deq_opts.reverse()
            for i in range(min(len(enq_opts), len(deq_opts))):
                if found_enq == 0:
                    if not i  >= len(enq_opts)-1:
                        e = enq_opts[i]
                        if nq_index[e] == 0:
                            nq_index[e] = i
                            found_enq = e        
                if found_deq == 0:
                    if not i >= len(deq_opts)-1:
                        d = deq_opts[i]
                        if dq_index[d] == 0:
                            dq_index[d] = i
                            found_deq = d
                if found_deq != 0 and found_enq != 0:
                    half_set_orders.update({i: (e,d)})
                    split_overlaps.pop(i)
                    break
    return split_overlaps, half_set_orders, nq_index, dq_index, inp

def assign_long_overlap(longs: dict, half_set: dict, nq_index, dq_index):# -> {longs,half_ass, nq_index, dq_index}:
    for k in longs.keys():
        is_set = False
        for i in longs[k]:
            if nq_index[i] == 0 and dq_index[i] == 0:
                nq_index[i] = k
                dq_index[i] = k
                half_set.update({k: (i,i)})
                longs.pop(i)
                set = True
                break
            else:
                pass
    return(longs, half_set, nq_index, dq_index)
        
def create_overlaps(inp):# -> {short_overlaps, long_overlaps, nones}: # DONE?
    for i in inp.keys():
        (enqs, deqs) = inp[i]
        overlap = ()
        for e in enqs:
            for d in deqs:
                if e == d:
                    overlap = overlap + tuple([e]) # add all overlapping timestamps to a tuple 
                #else: pass
        if overlap == (): # if there are no overlapping
            min = 10000
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
    for value in sort.keys():
        (pos, enqs, deqs) = sort[value]
        if len(pos) == 1:
            short_overlaps.update({value: (pos[0],pos[0])}) # add so that all tuples have length 2 (for enq, deq). 
        elif pos[-1] == None:
            nones.update({value: pos})
        elif len(pos) == 2:
            if abs(pos[0] - pos[1]) != -1:
                split_overlap.update({value: (pos[0], pos[1])}) # add the closest pair ones. to the 
        else:
            long_overlaps.update({value: pos})
    return short_overlaps, long_overlaps, split_overlap, nones

def preassign_no_deqs_at_end(no_deqs, half_set_orders, nq_index, dq_index): # DONE?
    for n in range(len(dq_index), len(nq_index)):
        for item in no_deqs.items():
            #print(item)
            if n in item[1] and nq_index[n] == 0:
                half_set_orders.update({item[0]: (n, None)})
                nq_index[n] = item[0]
                no_deqs.pop(item[0])
                break
    return no_deqs, half_set_orders, nq_index, dq_index
'''
        #populate the split ones 
        else: 
            temp_temp = dict()
            for value in sort.keys():
                if n in sort[value][0]: ## handle somehow that split keys are also taken. (index array?)
                    temp_temp.update({value: sort[value]})
                else: continue
            temp_temp = dict(sorted(inp.items(), key=lambda x:len(x[1][0])))
    
'''

''' def actual_run(inp):
    shorts, longs, no_deqs = create_overlaps(inp)
    nones = len(no_deqs)
    longs = sort(longs by len of overlap)
    no_deqs = sort(no_deqs by len of overlap)
    nq_index = [0]*len(inp)
    dq_index = [0]*(len(inp) - nones)
    sets = dict()
    half_set = dict()
    non_assigned = dict() #the ones you couldn't set in some function

    pre_assign_nones(nones, halfset, nq, dq) 
    assign_ones(shorts, sets, nq, dq) # should be first to be optimal

    assign_splits() ## cant unassign because that could split 
    assign_longs()
    assign_nones()

def assign_longs():
    for item in longs.item()
        kicked = item
        num = 0
        while kicked != None and num < 30 # perhaps 
            kicked = assign_long(kicked, half_sets): # kicked is an item that has to be reassigned to 
            num += 1
        if num >= 30 
            non_assigned.uppdate(kicked)


def assign_long(item):
    for pos in item[1]:
        if nq_index[pos] and dq_index[pos] == 0:
            half_set.updat(item)
            nq_ = item.key()
            dq_ = item.key()
            return None
    min = 1000
    nq, dq = None
    for n in nq_[pos[0], pos[-1]]
        if n == 0:
            for d in dq[pos[], pos[-1]]
                if d == 0:
                    if abs(n-d) < min:
                        nq = n
                        dq = d
                        min = abs(n-d)
    if nq and dq != None:
        half_set.updat(item)
            nq_ = item.key()5
            dq_ = item.key()
            return None
    else: 
        get inp of vals in range poss who share position. (vals can be gotten from nq and dq)
        sort by length reverse
        kick the one with most options 
        assign item to that position.
            set nq and dq

'''

