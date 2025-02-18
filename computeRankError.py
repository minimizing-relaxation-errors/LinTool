# SCRIPT DESCRIPTION
# Takes two dictionaries containing values : timestamps pairs
# puts is a dict of enqueues, gets is a dict of dequeues

def compute_rank_error(puts, gets):
	tot_rank_error = 0
	max_rank_error = 0

	# Sort by timestamp
	puts_sorted = dict(sorted(puts.items(), key=lambda x:x[1]))
	gets_sorted = dict(sorted(gets.items(), key=lambda x:x[1]))

	tot_get = len(gets)
	tot_put = len(puts)
	
	enq_length = len(puts)
	
	for deq_val, deq_timestamp in gets_sorted.items():
		rank_error = 0

		for enq_val, enq_timestamp in puts_sorted.items():
			if deq_val != enq_val: 
				rank_error += 1
			else: 
				#enq_start_index += 1
				puts_sorted.pop(enq_val)
				break

		tot_rank_error += rank_error
		if rank_error > max_rank_error:
			max_rank_error = rank_error

	mean_rank_error = tot_rank_error / tot_get

	print("Number of put operations: ", tot_put)
	print("Number of get operations: ", tot_get)
	print("Max rank error: ", max_rank_error)
	print("Total rank error: ", tot_rank_error)
	print("Mean rank error: ", mean_rank_error)