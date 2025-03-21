import pickle

class Timestamp:
    def __init__(self, enq_s, enq_e, deq_s, deq_e):
        self.enq_start = enq_s
        self.enq_end = enq_e
        self.deq_start = deq_s
        self.deq_end = deq_e
    # we know the enq times before the deq times so we have a function to add them later
    def update_deq(self, deq_s, deq_e):
        self.deq_start = deq_s
        self.deq_end = deq_e

    def update_enq(self, enq_s, enq_e):
        self.enq_end = enq_e
        self.enq_start = enq_s


def un_pickle(filename):
    picklename = "orders/" + filename +".pkl"
    with open(picklename, 'rb') as f:
        order_dict = pickle.load(f)
    return order_dict
