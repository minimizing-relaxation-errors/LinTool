'''Pseudokod rank error:

relax_stamp_t har värde och timestamp


sorterar gets efter timestamps
sortera puts efter timestamps

för varje enqueue:
	spara ett element med value och pekare till nästa i en lista

sista elementet i listan pekar på null
head är första elementet i listan

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

