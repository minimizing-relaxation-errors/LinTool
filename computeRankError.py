
"""
From d-CBO paper:
Consider the dequeue of item 𝑥 at time 𝑡 in a FIFO queue. 
Then the rank error becomes the number of items older than 𝑥 
in the queue at 𝑡, and the delay the number of items enqueued 
after the enqueue of 𝑥 that were dequeued before 𝑡.
"""

# putTimestamps: a dictionary of timestamps and values for each enqueue operation
# getTimestamps: a dictionary of timestamps and values for each dequeue operation
def compute_rank_error(puts, gets):
	tot_rank_error = 0
	max_rank_error = 0

	# Sort by timestamp
	puts_sorted = dict(sorted(puts.items(), key=lambda x:x[1]))
	gets_sorted = dict(sorted(gets.items(), key=lambda x:x[1]))

	tot_get = len(gets)
	

	tot_put = len(puts)
	

	print("Tot puts and gets: ", tot_get + tot_put)

	#enq_start_index = 0
	enq_length = len(puts)
	print(len(puts_sorted))
	
	for deq_val, deq_timestamp in gets_sorted.items():
		rank_error = 0

		for enq_val, enq_timestamp in puts_sorted.items():		# Sometimes gives max_rank_error which is one too high
		#for index in range(enq_start_index, enq_length-1):
			#enq_val, enq_timestamp  = list(puts.items())[index]
			if deq_val != enq_val: 
				rank_error += 1
			else: 
				#enq_start_index += 1
				puts_sorted.pop(enq_val)
				print(len(puts_sorted))
				break

		tot_rank_error += rank_error
		if rank_error > max_rank_error:
			max_rank_error = rank_error

	mean_rank_error = tot_rank_error / tot_get

	print("Tot get: ", tot_get)
	print("Tot puts: ", tot_put)
	print("Total rank error: ", tot_rank_error)
	print("Max rank error: ", max_rank_error)
	print("Mean rank error: ", mean_rank_error)



# TEST DATA -----------------------------------------------------------
# value : timestamp
"""puts = {
	1111 : 1,
	2222 : 2,
	3333 : 3,
	4444 : 4,
	5555 : 5
}

gets = {
	1111 : 6,	# rank error: 0
	4444 : 7,	# rank error: 2
	3333 : 8,	# rank error: 1
	2222 : 9,	# rank error: 0
	5555 : 10	# rank error: 0
}

compute_rank_error(puts, gets)"""