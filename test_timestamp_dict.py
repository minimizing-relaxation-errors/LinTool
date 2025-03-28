# Tests whether a timestamp dict has expected structure
# Takes as input decided enqueue timestamp dict, decided dequeue timestamp dict and original timestamp dict
# Outputs boolean (false if there is any error, true otherwise)

# TODO: Should maybe add a test to check if DIFFERENT timestamps (either enq or deq, but between different items) have the same timestamps
def test_timestamp_dict(e_decided_timestamps: dict, d_decided_timestamps: dict, original_timestamps: dict):
    # To store the operation values which are not within the allowed interval
    enq_not_within_interval = []
    deq_not_within_interval = []
    enq_not_before_deq = []
    enq_deq_same_timestamp = []

    # Test that decided enqueues are correct
    for (k, enq_timestamp) in e_decided_timestamps.items():
        e_start = original_timestamps[k].enq_start
        e_end = original_timestamps[k].enq_end
        d_start = original_timestamps[k].deq_end
        if(enq_timestamp > e_end or e_start > enq_timestamp): enq_not_within_interval.append("Value " + str(k) + ": " + str(e_start) + " < " + str(enq_timestamp) + " < " + str(e_end)) # Allow them to be equal

    # Test that decided dequeues are correct
    for (k, deq_timestamp) in d_decided_timestamps.items():
        d_start = original_timestamps[k].deq_start
        d_end = original_timestamps[k].deq_end
        if(deq_timestamp > d_end or d_start > deq_timestamp): deq_not_within_interval.append(k)
        if(e_decided_timestamps[k] > deq_timestamp): enq_not_before_deq.append(k)
        if(e_decided_timestamps[k] == deq_timestamp): enq_deq_same_timestamp.append(k)
   
    tests_passed = (len(enq_not_within_interval) + len(deq_not_within_interval) + 
            len(enq_not_before_deq) + len(enq_deq_same_timestamp)) == 0
    if(tests_passed): print("TEST: All timestamp dict tests passed!")
    else:
        print("TEST: Enqueue not within interval (op values): ", enq_not_within_interval)
        print("TEST: Dequeue not within interval (op values): ", deq_not_within_interval)
        print("TEST: Enqueue not before dequeue: ", enq_not_before_deq)
        print("TEST: Enqueue and dequeue have same timestamp: ", enq_deq_same_timestamp)

    return tests_passed