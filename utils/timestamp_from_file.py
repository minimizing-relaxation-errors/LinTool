import csv
from utils.timestamp import Timestamp

def get_timestamps_from_file(filename):
    timestamps = dict() ## initiate dict for timestamps
    with open("timestamps/" + filename, newline='') as csvfile:
                filereader = csv.reader(csvfile)
                for row in filereader:
                    ## if function is put (enqueue)
                    if row[2] == 'PUT':
                        if row[1] in timestamps.keys():
                            time = timestamps.get(row[1]) ## find existing timestamp object
                            time.update_enq(int(row[3]), int(row[4])) ## update timestamp with deq timestamps
                            timestamps.update({row[1]: time})
                        else: timestamps.update({row[1]: Timestamp(int(row[3]), int(row[4]), None, None)}) ## add value : (timestamp object with enq timestamps, also typecast to ints)
                    ## if function is get (dequeue)
                    elif row[2] == 'GET':
                        if row[1] in timestamps.keys():
                            time = timestamps.get(row[1]) ## find existing timestamp object
                            time.update_deq(int(row[3]), int(row[4])) ## update timestamp with deq timestamps
                            timestamps.update({row[1]: time}) ## update dict with all timestamps
                        else: timestamps.update({row[1]: Timestamp(None, None, int(row[3]), int(row[4]))})
    return timestamps