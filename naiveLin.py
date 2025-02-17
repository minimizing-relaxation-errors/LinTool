#from linearizationTool import Timestamp

def naive_lin(inp: dict):
    puts = dict()
    gets = dict()
    for i in inp:
        timestamp = inp[i]
        puts.update({i: timestamp.enq_start})
        if timestamp.deq_start != None:
            gets.update({i: timestamp.deq_start})

    return (puts,gets)