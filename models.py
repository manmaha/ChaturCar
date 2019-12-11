
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

class Naive_Model(Models):
    def __init__(self,args):
        super(Naive_Model,self).__init__(args)
    def generate_category(self,data):
        return 7
