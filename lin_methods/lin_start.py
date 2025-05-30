def naive_start(inp: dict):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
        enq_s = timestamp.enq_start
        deq_s = timestamp.deq_start
        enq_e = timestamp.enq_end
        deq_e = timestamp.deq_end
        if deq_s != None:
            if enq_s == deq_s and deq_e > deq_s:  deq_s += 1
            elif enq_s > deq_s and enq_e > deq_s: deq_s = enq_s + 1
            gets.update({i: deq_s})
        puts.update({i: enq_s})

    return (puts,gets)