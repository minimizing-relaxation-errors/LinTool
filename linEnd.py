
def naive_end(inp: dict):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
        puts.update({i: timestamp.enq_end})
        if timestamp.deq_end != None:
            gets.update({i: timestamp.deq_end})

    return (puts,gets)