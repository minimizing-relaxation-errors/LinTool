

def naive_two_five(inp: dict ):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
        mid = (timestamp.enq_start*3 + timestamp.enq_end) / 4
        puts.update({i: mid})
        if timestamp.deq_start != None:
            mid = (timestamp.deq_start*3 + timestamp.deq_end) / 4
            gets.update({i: mid})
    return (puts, gets)

