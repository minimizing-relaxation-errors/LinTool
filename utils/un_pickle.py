import pickle 

def un_pickle(foldername, filename):
    picklename = foldername + "/" + filename +".pkl"
    with open(picklename, 'rb') as f:
        order_dict = pickle.load(f)
    return order_dict
