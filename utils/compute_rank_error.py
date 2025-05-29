# SCRIPT DESCRIPTION
# Takes puts dictionary {item:enq_point} and gets dictionary {item:deq_point}
# Assumes gets do not include None (simply do not include the dequeue if it is None)

def compute_rank_error(puts, gets):
	tot_rank_error = 0
	max_rank_error = 0

	# Sort by timestamp
	puts_sorted = dict(sorted(puts.items(), key=lambda x:x[1]))
	gets_sorted = dict(sorted(gets.items(), key=lambda x:x[1]))

	tot_get = len(gets)
	tot_put = len(puts)
	
	rank_error_list = []
	
	for deq_val in gets_sorted.keys():
		rank_error = 0

		for enq_val in puts_sorted.keys():
			if deq_val != enq_val: 
				rank_error += 1
			else: 
				puts_sorted.pop(enq_val)
				break

		rank_error_list.append(rank_error)

		tot_rank_error += rank_error
		if rank_error > max_rank_error:
			max_rank_error = rank_error

	mean_rank_error = tot_rank_error / tot_get

	rank_error_variance = 0
	for err in rank_error_list:
		off = err - mean_rank_error
		rank_error_variance += (off * off)
    
	rank_error_variance = rank_error_variance / (tot_get - 1)

	return (tot_put, tot_get, tot_rank_error, max_rank_error, mean_rank_error, rank_error_variance)