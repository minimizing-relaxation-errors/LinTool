from timestamp import Timestamp
import datetime
from timestamp_from_file import get_timestamps_from_file
import pickle
import os
import sys

# TODO: Maybe we should create a util script to do this, which can be imported by other util scripts
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Cursed
sys.path.append(parent_path)
from linearization_tool import get_timestamps_from_file
sys.path.remove(parent_path)

def ordering_reduction(inp: dict):
    reduce = dict() # dict of value and potential indices
    for i in inp.keys(): ## the algorithm is essentially: 
        nr_fin_before_e = 0
        nr_fin_before_d = 0
        nr_overlap_e = 0
        nr_overlap_d = 0
        attempt = 0
        bös = 0
        for j in inp.keys():
            if i != j: # (don't compare against ourselves)
                if inp[j].enq_end <= inp[i].enq_start: # how many timestamps of the same typ have ended before our item
                    nr_fin_before_e +=1
                elif inp[j].enq_start >= inp[i].enq_end: # to get overlapping we see which ones end after

                    pass
                else: # and the rest are overlapping and should be included in our count
                    nr_overlap_e +=1
                if inp[i].deq_start == None:
                    pass
                elif inp[j].deq_start == None:
                    continue
                else: # make sure that both items have been dequeued
                    if inp[j].deq_end <= inp[i].deq_start: # then we do the same for dequeues so each ordering starts at 0
                        nr_fin_before_d +=1
                    elif inp[j].deq_start >= inp[i].deq_end:
                        pass
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

def is_valid_order(inp: dict): ## takes in reduced dict as returned from ordering reduction
    no_missing_pos = False
    feasible_positions = True
    num = 0
    enq_poss = set()
    deq_poss = set()
    missing = []
    for i in inp.keys():
        (enqs, deqs) = inp[i]
        for e in enqs:
            enq_poss.add(e)
        for d in deqs:
            if d != None:
                deq_poss.add(d)
    for i in range(max(enq_poss)):
        if not i in enq_poss:
            missing.append(("enq", i))
    for i in range(max(deq_poss)):
        if not i in deq_poss:
            missing.append(("deq", i))   
    if missing == []:
        no_missing_pos = True

    for i in inp.keys():
        (ienqs, ideqs) = inp[i]
        if len(ienqs) == 1:
            for o in inp.keys():
                if i!=o:
                    (oenqs, odeqs) = inp[o]
                    if len(oenqs)  == 1:
                        if oenqs[0] == ienqs[0]:
                            feasible_positions = False
                            num = oenqs[0]
                            break
                    else: continue
            
        elif len(ideqs) == 1:
            if ideqs[0] == None:
                continue
            else:
                for o in inp.keys():
                    if i!=o:
                        (oenqs, odeqs) = inp[o]
                        if len(odeqs) == 1:
                            if odeqs[0] == None:
                                continue
                            else:    
                                if odeqs[0] == ideqs[0]:
                                    feasible_positions = False
                                    num = odeqs[0]
                                    break
                        else: continue

        else: continue
    return feasible_positions, num, no_missing_pos, missing, 

def main():
    print(datetime.datetime.now())
    files = ["short-10-2ddo-d2-n32-w32-l32_1.csv",
             "short-10-dcbo-d2-n32-w32-c2_1.csv",
             "short-10-faaaq-d2-n32_1.csv"] # also change import in timestamp_from_file.py to commented out one and then back again when running linearizations

    for filename in files:
        ordername = "orders/" + filename +".pkl"
        file = get_timestamps_from_file(filename)
        red = ordering_reduction(file)
        (feas, num, bmiss, miss) = is_valid_order(red)
        with open(ordername, 'wb') as f:
            pickle.dump(red, f)
        print(datetime.datetime.now())
        print(feas, num, bmiss, miss)

if __name__== "__main__":
    main()