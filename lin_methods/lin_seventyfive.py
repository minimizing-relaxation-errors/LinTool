def naive_seven_five(inp: dict ):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
       
        at_third_quarter_enq = (timestamp.enq_start + timestamp.enq_end*3) / 4
        if timestamp.deq_start != None:
            at_third_quarter_deq = (timestamp.deq_start + timestamp.deq_end*3) / 4
            if at_third_quarter_enq >= at_third_quarter_deq and at_third_quarter_enq < timestamp.deq_end: at_third_quarter_deq = at_third_quarter_enq + 1
            gets.update({i: at_third_quarter_deq})
        puts.update({i: at_third_quarter_enq})

    return (puts, gets)