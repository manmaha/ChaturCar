
'''
Contains Implementations for Models for Generating ChaturCar commands
input = data (image)
output = commands = [steer,drive]
Manish Mahajan
26 Sep 2019
'''
class Models(object):
    def __init__(self,args):
        pass

class Naive_Model(Models):
    def __init__(self,args):
        super(Naive_Model,self).__init__(args)
    def generate_commands(self,data):
        return [0.0,0.0]
