from timestamp import Timestamp

''' # small test case with known ordering (works)
test = {
    1: Timestamp(301, 308, 312, 318),
    2: Timestamp(303, 311, 313, 317),
    3: Timestamp(306, 312, 315, 320),
    4: Timestamp(310, 315, 319, 322)
}
'''



def ordering_reduction(inp: dict):
    inp = dict(sorted(inp.items(), key=lambda x:x[1].enq_start)) # at this point this is kindof useless but it could be used to reduces the number of js we look at (from start untill all overlapped are passed or something)
    reduce = dict() # dict of value and potential indices
    for i in inp.keys(): ## the algorithm is essentially: 
        nr_fin_before_e = 0
        nr_fin_before_d = 0
        nr_overlap_e = 0
        nr_overlap_d = 0
        attempt = 0
        for j in inp.keys():
            if i != j: # (don't compare against ourselves)
                if inp[j].enq_end < inp[i].enq_start: # how many timestamps of the same typ have ended before our item
                    nr_fin_before_e +=1
                elif inp[j].enq_start > inp[i].enq_end: # to get overlapping we see which ones end after
                    #attempt += 1
                    #if attempt > 10000:
                    #    break
                    continue
                else: # and the rest are overlapping and should be included in our count
                    nr_overlap_e +=1
                if inp[i].deq_start != None and inp[j].deq_start != None:
                    if inp[j].deq_end < inp[i].deq_start: # then we do the same for dequeues so each ordering starts at 0
                        nr_fin_before_d +=1
                    elif inp[j].deq_start > inp[i].deq_end:
                        #attempt += 1
                        #if attempt > 10000:
                        #    break
                        continue
                    else: 
                        nr_overlap_d +=1

        enq_ord = [x for x in range(nr_fin_before_e, nr_fin_before_e+ nr_overlap_e+1)] #construct the potential indicies
        if inp[i].deq_start != None:
            deq_ord = [x for x in range(nr_fin_before_d, nr_fin_before_d+nr_overlap_d+1)]
        else: 
            deq_ord = [None]
        reduce.update({i: (enq_ord, deq_ord)}) #add to dictionary with same key (we're still in the loop)
    return reduce

                


def timestamp_reduction(inp: dict):
    allStamps = []
    for i in inp.keys():
        timestamp = inp[i]
        allStamps.extend([timestamp.enq_start, timestamp.enq_end])
        if timestamp.deq_start != None:
            allStamps.extend([timestamp.deq_start, timestamp.deq_end])
    allStamps.sort()
    reducedStamps = dict()
    for i in inp:
        time = inp[i]
        enq_s = allStamps.index(time.enq_start)
        enq_e = allStamps.index(time.enq_end)
        if time.deq_start != None:
            deq_s = allStamps.index(time.deq_start)
            deq_e = allStamps.index(time.deq_end)
            redTime = Timestamp(enq_s, enq_e, deq_s, deq_e)
        else: 
            redTime = Timestamp(enq_s, enq_e, None, None)
        reducedStamps.update({i: redTime})
    return reducedStamps

