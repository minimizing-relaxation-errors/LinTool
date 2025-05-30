def naive_end(inp: dict):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
        enq_s = timestamp.enq_start
        deq_s = timestamp.deq_start
        enq_e = timestamp.enq_end
        deq_e = timestamp.deq_end
        if deq_e != None:
            if enq_e >= deq_e and deq_e > enq_s: enq_e = deq_e - 1
            gets.update({i: deq_e})
        puts.update({i: enq_e})

    return (puts,gets)