

def naive_seven_five(inp: dict ):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
        at_third_quarter = (timestamp.enq_start + timestamp.enq_end*3) / 4
        puts.update({i: at_third_quarter})
        if timestamp.deq_start != None:
            at_third_quarter = (timestamp.deq_start + timestamp.deq_end*3) / 4
            gets.update({i: at_third_quarter})
    return (puts, gets)

