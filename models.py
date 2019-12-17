import numpy as np
import tensorflow as tf
import os
from yaml import load, Loader, dump
import argparse

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

class Trained_Model(Models):
    def __init__(self,args):
        super(trained_Model,self).__init__(args)
        self.model = tf.keras.models.load_model(os.path.join(self.args.modelpath,self.args.modelfile))
    def predict_category_proba(self,data):
        x = x/255
        x = np.exapnd_dims(x,axis=0)
        return model.predict(x)




def main():
	params = load(open('ChaturCar.yaml').read(), Loader=Loader)
	parser = argparse.ArgumentParser(description='Models')
    parser.add_argument('--modelpath', default=params['modelpath'])
    parser.add_argument('--modelfile', default=params['modelfile'])
	args = parser.parse_args()
	m = Trained_Model(args)
	c.collect_data()
if __name__=="__main__":
        main()
