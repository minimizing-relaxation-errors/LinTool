# Tests whether a timestamp dict has expected structure
# Takes as input decided enqueue timestamp dict, decided dequeue timestamp dict and original timestamp dict
# Outputs boolean (false if there is any error, true otherwise)

# Expects all decided timestamps to exist, no None values
def test_timestamp_dict(e_decided_timestamps: dict, d_decided_timestamps: dict, original_timestamps: dict):
    # To store the operation values which are not within the allowed interval
    enq_not_within_interval = []
    deq_not_within_interval = []
    enq_not_before_deq = []
    enq_deq_same_timestamp = []

    # Tests that decided enqueues are correct
    for (item, enq_timestamp) in e_decided_timestamps.items():
        e_start = original_timestamps[item].enq_start
        e_end = original_timestamps[item].enq_end
        d_start = original_timestamps[item].deq_end
        if(enq_timestamp > e_end or e_start > enq_timestamp): enq_not_within_interval.append("Value " + str(item) + ": " + str(e_start) + " < " + str(enq_timestamp) + " < " + str(e_end)) # Allow them to be equal

    # Tests that decided dequeues are correct
    for (item, deq_timestamp) in d_decided_timestamps.items():
        d_start = original_timestamps[item].deq_start
        d_end = original_timestamps[item].deq_end
        if d_end == None or d_start == None: continue # If dequeue None then do not test dequeue timestamp TODO: Maybe we should test that it is at a valid place?
        if(deq_timestamp > d_end or d_start > deq_timestamp): deq_not_within_interval.append(item)
        if(e_decided_timestamps[item] > deq_timestamp): enq_not_before_deq.append(item)
        if(e_decided_timestamps[item] == deq_timestamp): enq_deq_same_timestamp.append(item)

    # output data init
    out_str = ""
    tests_passed = (len(enq_not_within_interval) + len(deq_not_within_interval) + 
            len(enq_not_before_deq) + len(enq_deq_same_timestamp)) == 0 
    
    # Tests that all timestamps are unique
    all_timestamps = []
    all_timestamps.extend([enq for enq in e_decided_timestamps.values()])
    all_timestamps.extend([deq for deq in d_decided_timestamps.values()])
    unique_timestamps = set(all_timestamps)
    if len(all_timestamps) != len(unique_timestamps):
        tests_passed = False
        out_str += "Multiple timestamps: " + str(abs(len(all_timestamps)-len(unique_timestamps))) + "\n"

    out_str += ("Enqueue not within interval (op values): " + str(enq_not_within_interval) + "\n" +
                "Dequeue not within interval (op values): " + str(deq_not_within_interval) + "\n" +
               "Enqueue not before dequeue: " + str(enq_not_before_deq) + "\n" +
               "Enqueue and dequeue have same timestamp: " + str(enq_deq_same_timestamp))

    return (tests_passed, out_str)