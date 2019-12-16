import numpy as np
'''
Contains Implementations for Models for Generating ChaturCar commands
input = data (image)
output = Category = 1 to 7
Manish Mahajan
26 Sep 2019
'''
class Models(object):
    def __init__(self,args):
        pass
    def predict_category(self,data):
        return(np.argmax(self.predict_category_proba(data)))

class Naive_Model(Models):
    def __init__(self,args):
        super(Naive_Model,self).__init__(args)
    def predict_category_proba(self,data):
        prob_array = np.random.random(7)
        return prob_array/np.sum(prob_array)
