# Script to test two timestamp files against each other
# One has start- and end times fpr each operation and the other only has a single timestamp per operation

import csv

# Takes as input two input lists: start_end and single
# Assumes both lists are of equal length and that each list contains:
# tuples with operation value, operation type and two or one timestamps respecitvely,
# and that each index contains the corresponding timestamp in both files
# Returns lists of values before the interval, after the interval and tuples of values which do not match although they should
def test_timestamp_between_start_end(start_end, single):
    values_before = []
    values_after = []
    non_matching_values = []
    for index, (value_1, op_1, start, end) in enumerate(start_end):
        (value_2, op_2, time) = single[index]
        if value_1 != value_2: 
            #print("NOT EQUAL: ", value_1, value_2, " AT INDEX ", index)
            non_matching_values.append((value_1, value_2))
        elif time < start:
            values_before.append(value_2)
        elif time > end:
            values_after.append(value_2)
    return (values_before, values_after, non_matching_values)

if __name__=="__main__":
    timestamp_filenames = ["dcbo-timestamps-196790479664.csv"]
    first_foldername = "timestamps"
    second_foldername = "current_linearization_results"

    for file in timestamp_filenames:
        start_end = []
        single = []
        # Collect start and end timestamps
        with open("../" + first_foldername + "/" + file, newline='') as csvfile:
            filereader = csv.reader(csvfile)
            for row in filereader:
                start_end.append((row[1], row[2], row[3], row[4]))
        with open("../" + second_foldername + "/" + file, newline='') as csvfile:
            filereader = csv.reader(csvfile)
            for row in filereader:
                single.append((row[1], row[2], row[3]))

        print("FILENAME: ", file)
        print("CHECK start_end length == single length: ", len(start_end) == len(single))
        (values_before, values_after, non_matching_values) = test_timestamp_between_start_end(start_end, single)

        print("TEST nr of values with single timestamp BEFORE start-end interval: ", len(values_before))
        print("TEST nr of values with single timestamp AFTER start-end interval: ", len(values_after))
        print("TEST nr of nonmatching value tuples: ", len(non_matching_values), "\n")