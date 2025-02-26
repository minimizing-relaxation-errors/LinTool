

def naive_two_five(inp: dict ):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
        at_first_quarter = (timestamp.enq_start*3 + timestamp.enq_end) / 4
        puts.update({i: at_first_quarter})
        if timestamp.deq_start != None:
            at_first_quarter = (timestamp.deq_start*3 + timestamp.deq_end) / 4
            gets.update({i: at_first_quarter})
    return (puts, gets)

