def naive_two_five(inp: dict ):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
        at_first_quarter_enq = (timestamp.enq_start*3 + timestamp.enq_end) / 4
        if timestamp.deq_start != None:
            at_first_quarter_deq = (timestamp.deq_start*3 + timestamp.deq_end) / 4
            if at_first_quarter_enq >= at_first_quarter_deq and at_first_quarter_enq < timestamp.deq_end: at_first_quarter_deq = at_first_quarter_enq + 1
            gets.update({i: at_first_quarter_deq})
        puts.update({i: at_first_quarter_enq})
    return (puts, gets)