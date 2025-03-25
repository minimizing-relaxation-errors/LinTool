# Expects timestamp dict of form: { value: Timestamp(enq start timestamp, enq end timestamp, deq start timestamp, deq end timestamp)}
# Expects ordering dict of form: {value: enq order, deq order}
# Outputs two dictionaries, one for enq and one for deq, each of the form {value : timestamp}
# NOTE: Not testet yet
def order_to_timestamp(timestamp_dict: dict, ordering_dict: dict):

    gets = {}
    puts = {}

    sorted_ordering_dict = {k: v for k, v in sorted(ordering_dict.items(), key=lambda item: item[1][0])} # Sort on enq_order (ascending)
    latest_timestamp = 0 # Assumes positive time
    for (key, v) in sorted_ordering_dict.items():
        e_start = timestamp_dict[key].enq_start
        d_end = timestamp_dict[key].deq_end

        e_lin = latest_timestamp + 1
        if e_start > e_lin: e_lin = e_start
        if e_lin > d_end: raise Exception("Error: Incorrect timestamp or ordering file")
        latest_timestamp = e_lin
        puts[key] = e_lin

    sorted_ordering_dict = {k: v for k, v in sorted(ordering_dict.items(), key=lambda item: item[1][1])} # Sort on deq_order (ascending)
    latest_timestamp = 0 # Reset time
    for (key, v) in sorted_ordering_dict.items():
        d_start = timestamp_dict[key].deq_start
        d_end = timestamp_dict[key].deq_end

        d_lin = latest_timestamp + 1
        if d_start > d_lin: d_lin = d_start
        if puts[key] > d_lin: d_lin = puts[key] + 1
        if d_lin > d_end: raise Exception("Error: Incorrect timestamp or ordering file")
        latest_timestamp = d_lin

        gets[key] = d_lin

    return (puts, gets)