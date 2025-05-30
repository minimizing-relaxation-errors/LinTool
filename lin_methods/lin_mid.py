def naive_mid(inp: dict ):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
        mid_enq = (timestamp.enq_start + timestamp.enq_end)/2
        if timestamp.deq_start != None:
            mid_deq = (timestamp.deq_start + timestamp.deq_end) / 2
            if mid_enq >= mid_deq and mid_enq < timestamp.deq_end: mid_deq = mid_enq + 1
            gets.update({i: mid_deq})
        puts.update({i: mid_enq})
    return (puts, gets)