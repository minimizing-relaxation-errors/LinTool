# Expects timestamp dict of form: { value: Timestamp(enq start timestamp, enq end timestamp, deq start timestamp, deq end timestamp)}
# Expects ordering dict of form: {value: enq order, deq order}
# Outputs two dictionaries, one for enq and one for deq, each of the form {value : timestamp}
# NOTE: There is no guarantee that there will be an output. May cast exception due to selected ordering that is inputted here.
def order_to_timestamp(timestamp_dict: dict, ordering_dict: dict):

    gets = {}
    puts = {}

    sorted_ordering_dict = {k: v for k, v in sorted(ordering_dict.items(), key=lambda item: item[1][0])} # Sort on enq_order (ascending)
    latest_timestamp = 0
    for (key, v) in sorted_ordering_dict.items():
        #print(" 🤏🤏",key, ordering_dict[key])
        e_start = timestamp_dict[key].enq_start
        d_end = timestamp_dict[key].deq_end

        e_lin = latest_timestamp + 0.01
        if e_start > e_lin: e_lin = e_start
        if d_end != None:
            if e_lin > d_end: 
                print(key)
                raise Exception("Error: Incorrect timestamp or ordering dict")
        latest_timestamp = e_lin
        puts[key] = e_lin
    #print("PUTS: ", puts, "\n")
 #   keys = ordering_dict.keys()
 #   for k in keys:
 #       if ordering_dict[k][1] == None:
 #           ordering_dict.pop(k)
    no_none = {k:v for k,v in ordering_dict.items() if v[1] != None}
    sorted_ordering_dict = {k: v for k, v in sorted(no_none.items(), key=lambda item: item[1][1]) } # Sort on deq_order (ascending)
    latest_timestamp = 0 # Reset time
    for (key, v) in sorted_ordering_dict.items():
        d_start = timestamp_dict[key].deq_start
        d_end = timestamp_dict[key].deq_end

        d_lin = latest_timestamp + 0.01
        if d_start > d_lin: 
            d_lin = d_start
        if puts[key] > d_lin: 
            d_lin = puts[key] + 0.01
        if d_lin > d_end: 
            print("item:", key, "order", v[1], "⤵️Enq linearization point", puts[key],"⤴️deq linearization point", d_lin, "start: ", d_start," end: ", d_end )
            raise Exception("Error: Incorrect timestamp or ordering dict")
        latest_timestamp = d_lin
        #print("item:", key, "order", v[1], "⤵️Enq linearization point", puts[key],"⤴️deq linearization point", d_lin, "start: ", d_start," end: ", d_end )
        gets[key] = d_lin

    return (puts, gets)