from timestamp import Timestamp

''' # small test case with known ordering (works)
test = {
    1: Timestamp(301, 308, 312, 318),
    2: Timestamp(303, 311, 313, 317),
    3: Timestamp(306, 312, 315, 320),
    4: Timestamp(310, 315, 319, 322)
}
'''
 # slightly larger test for ordering, including None deq values (works)
test = {
    1: Timestamp(1,6,21,32),
    2: Timestamp(2,10,16,27),
    3: Timestamp(5,7,30,38),
    4: Timestamp(14, 24, 35, 39),
    5: Timestamp(20, 34, 43, 44),
    6: Timestamp(29, 37, None, None),
    7: Timestamp(9,13, 23,33),
    8: Timestamp(12,17, 40, 45),
    9: Timestamp(4,11, 25, 36),
    10: Timestamp(15, 22, 31, 41),
    11: Timestamp(41, 46, None, None),
    12: Timestamp(19, 26, 36, 40),
    13: Timestamp(3, 8, 18, 28),
    14: Timestamp(47, 48, 50, 50),
    17: Timestamp(44, 45, 50, 50),
    15: Timestamp(47, 48, 50, 50),
    16: Timestamp(46, 47, 49, 50),
    18: Timestamp(44,45,46,51),
    19: Timestamp(31, 33, 45, 51),
    #820237: Timestamp(321728, 321984, 670400, 670912),
    #818692: Timestamp(321216, 321472, 670144, 670656),
    #820737: Timestamp(322240, 322496, 670656, 670656),
    #819717: Timestamp(334016, 334272, 670656, 670656),
    #821258: Timestamp(338368, 338624,  670656, 670656),
    #805390: Timestamp(339904, 340416, 671680, 670912),
    #808203: Timestamp(340672, 340928, 671168, 670912),
    238089: Timestamp(1742310392178550528,1742310392178550784,1742310392178797824,1742310392178797568),
    245510: Timestamp(1742310392178569216,1742310392178569472,1742310392178798336,1742310392178797824),
    241163: Timestamp(1742310392178555392,1742310392178555392,1742310392178798336,1742310392178797824),
}

test2 = {
    1 : Timestamp(0, 5, 20, 32),
    2 : Timestamp(1, 9, 15, 26),
    3 : Timestamp(4, 6, 29, 40),
    4 : Timestamp(13, 23, 36, 41),
    5 : Timestamp(19, 35, 46, 47),
    6 : Timestamp(28, 39, None, None),
    7 : Timestamp(8, 12, 22, 33),
    8 : Timestamp(11, 16, 42, 50),
    9 : Timestamp(3, 10, 24, 37),
    10 : Timestamp( 14, 21, 30, 44),
    11 : Timestamp(44, 54, None, None),
    12 : Timestamp(18, 25, 37, 42),
    13 : Timestamp(2, 7, 17, 27),

    14 : Timestamp(159, 160, 163, 163),
    17 : Timestamp(147, 150, 163, 163),
    15 : Timestamp(157, 160, 163, 163),
    16 : Timestamp(154, 157, 161, 163),
    18 : Timestamp(147, 150, 164, 170),
    19 : Timestamp(130, 132, 165, 170),
    20 : Timestamp(131, 133, 166, 170),
    820737 : Timestamp(76, 77, 88, 88),
    819717 : Timestamp(78, 79, 88, 88),
    821258 : Timestamp(80, 81, 88, 88),
    818692 : Timestamp(72, 73, 86, 88),
    820237 : Timestamp(74, 75, 87, 95),
    808203 : Timestamp(84, 85, 98, 95),
    805390 : Timestamp(82, 83, 99, 95),
}


def ordering_reduction(inp: dict):
    #inp = dict(sorted(inp.items(), key=lambda x:x[1].enq_start)) # at this point this is kindof useless but it could be used to reduces the number of js we look at (from start untill all overlapped are passed or something)
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
                if inp[j].enq_end < inp[i].enq_start: # how many timestamps of the same typ have ended before our item
                    nr_fin_before_e +=1
                elif inp[j].enq_start > inp[i].enq_end: # to get overlapping we see which ones end after
                    #attempt += 1
                    #if attempt > 10000:
                    #    break
                    pass
                else: # and the rest are overlapping and should be included in our count
                    nr_overlap_e +=1
                if inp[i].deq_start == None:
                    pass
                elif inp[j].deq_start == None:
                    continue
                else: # make sure that both items have been dequeued
                    if inp[j].deq_end < inp[i].deq_start: # then we do the same for dequeues so each ordering starts at 0
                        nr_fin_before_d +=1
                        #print("ends before", i, j, inp[j].deq_end, inp[i].deq_start)
                    elif inp[j].deq_start > inp[i].deq_end:
                        #attempt += 1
                        #if attempt > 10000:
                        #    break
                        #print("starts after", i, j, inp[j].deq_start, inp[i].deq_end)   
                        pass
                    else: 
                        nr_overlap_d +=1
                        #print(i, j, nr_overlap_d)
                        

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
    blorb = timestamp_reduction(test)
    for b in blorb:
        #print(b, blorb[b])
        print(b,":", blorb[b].enq_start, blorb[b].enq_end, blorb[b].deq_start, blorb[b].deq_end)

    #print(is_valid_order(blorb))

if __name__== "__main__":
    main()