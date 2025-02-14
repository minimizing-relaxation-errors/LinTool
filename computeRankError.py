'''Typ pseudokod rank error:

relax_stamp_t har värde och timestamp

sorterar gets efter timestamps
sortera puts efter timestamps

för varje enqueue:
	spara ett element med value och pekare till nästa i en lista

sista elementet i listan pekar på null
head pekar på första elementet i listan (dess värde)

for varje dequeue:
	ta värdet (key) från dequeue-elementet
	om head == key
		head = head->next
		rank_error = 0
	annars
		rank_error = 1
		current = head
		medan current->next inte är key
			current = current->next
			rank_error += 1
			om current->next == NULL så finns inte objected, ge error och exita
		current->next = current->next->next // unlink current-next från datastrukturen

	rank_error_sum += rank_error
	if rank_error > rank_error_max
		rank_error_max = rank_error'''

# putTimestamps: a dictionary of timestamps and values for each enqueue operation
# getTimestamps: a dictionary of timestamps and values for each dequeue operation
def compute_rank_error(put_timestamps, get_timestamps):

	# Sort by timestamp
	put_timestamps = dict(sorted(put_timestamps.items()))
	get_timestamps = dict(sorted(get_timestamps.items()))

	print(put_timestamps)
	print(get_timestamps)

	rank_error_sum = 0
	rank_error_max = 0

	putLen = len(put_timestamps)

	i = 0 #first index in put_timestamp list

	#for each dequeue
	for idx, dts in enumerate(get_timestamps): # om vi inte behöver index så bör detta nog ändras till något där vi kan få värdet direkt
		key = get_timestamps.get(dts)	# Get value
		rank_error = 0

		#while i < putLen:
			



	#for keys, value in put_timestamps.items():
		#print(keys)
		#print(value[0])


		
	
	'''enq_ind = 0
	for get_ind, get_row in get_timestamps.iterrows():
		
		#key = row["value"]
		for put_ind, put_row in put_timestamps.iterrows():
			print("put row val: " + str(put_row['value']))
			print("get row val: " + str(get_row['value']))
			if(get_row['value'] == put_row['value']):
				print("EQUAL!")
				break
			else:
				rank_error += 1

		rank_error_sum += rank_error
		if rank_error > rank_error_max:
			rank_error_max = rank_error'''

		#if(put_timestamps[0]["value"] == key)
		#print(row["timestamp"])

	print("Rank error sum: " + str(rank_error_sum))
	print("Rank error max: " + str(rank_error_max))




# TEST DATA -----------------------------------------------------------
# timestamp : value
put_timestamps = {
	1 : 1111,
	2 : 2222,
	3 : 3333,
	4 : 4444,
	5 : 5555
}

get_timestamps = {
	6 : 1111,
	7 : 4444,	# should be fourth to be dequeued
	8 : 3333,
	9 : 2222,	# should be second to be dequeued
	10 : 5555
}

compute_rank_error(put_timestamps, get_timestamps)