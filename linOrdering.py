from timestamp import un_pickle

def ordering_lin(filename):
    inp = dict()
    inp = un_pickle(filename)
    ## do a first pass to see "good positions" based on overlapping with 
    for i in inp.keys():
        (enqs, deqs) = inp[i]
        overlap = ()
        for e in enqs:
            for d in deqs:
                if e == d:
                    overlap = overlap + tuple([e])
                #else: pass
        if overlap ==():
            min = 10000
            for e in enqs:
                for d in deqs:
                    if d != None:
                        if abs(int(e)-int(d)) < min:
                            min = abs(e-d)
                            overlap = (e,d)
                    else: 
                        overlap = tuple(enqs)

        inp.update({i:(overlap, enqs, deqs)})
    sort = dict(sorted(inp.items(), key=lambda x:len(x[1][0])))
    temp_res = dict()
    long_overlaps = dict()
    for value in sort.keys():
        (pos, enqs, deqs) = sort[value]
        if len(pos) == 1:
            temp_res.update({value: (pos[0],pos[0])})
        elif len(pos) == 2:
            if abs(pos[0] - pos[1]) != 1:
                temp_res.update({value: (pos[0], pos[1])})
        else:
            long_overlaps.update({value: sort[value]})
    for n in range(len(inp)):
        if (n,n) in temp_res.values():
            continue
        else: 
            temp_temp = dict()
            for value in sort.keys():
                if n in sort[value][0]: ## handle somehow that split keys are also taken. (index array?)
                    temp_temp.update({value: sort[value]})
                else: continue
            temp_temp = dict(sorted(inp.items(), key=lambda x:len(x[1][0])))
    
