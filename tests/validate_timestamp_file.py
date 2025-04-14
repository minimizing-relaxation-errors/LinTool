# SCRIPT DESCRIPTION
# Checks if there are any duplicate values in a timestamp file.
# Script takes filename as input.

def check_duplicate_values_timestamp_file(filename, timestamps):
    enq_fails = 0
    deq_fails = 0
    deq_end_enq_start_fails = 0
    for key in timestamps:
        timestamp = timestamps[key]
        # "Asserts" enqueue start is before enqueue end
        if timestamp.enq_start > timestamp.enq_end:
            #print("ENQ FAIL! ", key)
            enq_fails += 1
        # "Asserts" that dequeue start is before dequeue end
        if timestamp.deq_start != None:
            if timestamp.deq_start > timestamp.deq_end:
                deq_fails += 1
        # "Asserts" that dequeue end is after enqueue start
        if timestamp.deq_end is not None:
            if timestamp.deq_end < timestamp.enq_start:
                deq_end_enq_start_fails += 1

    keys = []
    for key in timestamps.keys():
        keys.append(key)
    unique_keys = set(keys)
    key_occ = {}
    for key in unique_keys:
        # Checks if our values (keys in timestamp file) are unique
        occ = keys.count(key)
        key_occ[key] = occ

    duplicates = {}
    for key, value in key_occ.items():
        if(value > 2):      # Expects at most 2 occurances of the same value, one for enq and one for potential dequeue
            duplicates[key] = value
            print("Key: ", key, " occurs ", value, " times across both enq and deq operations")

    print("Number of duplicate values: ", len(duplicates))
    print("Number of DEQ ends before ENQ starts: ", deq_end_enq_start_fails)
    print("Number of ENQ ends before starts: ", enq_fails)
    print("Number of DEQ ends before starts: ", deq_fails)

    print("Finished checking file: ", filename)