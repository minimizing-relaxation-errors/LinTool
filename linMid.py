

def naive_mid(inp: dict ):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
        mid = (timestamp.enq_start + timestamp.enq_end)/2
        puts.update({i: mid})
        if timestamp.deq_start != None:
            mid = (timestamp.deq_start + timestamp.deq_end) / 2
            gets.update({i: mid})
    return (puts, gets)

