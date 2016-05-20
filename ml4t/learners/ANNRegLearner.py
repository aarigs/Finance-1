##"""
##A wrapper for neural network regression. 
##"""
##print "Not currently in production. Sorry"
##exit()

import numpy as np
from NeuralNetwork2 import *

class ANNRegLearner(object):

    def __init__(self, sizes=[], verbose = False):
        self.name = "Neural net Regression Learner"
        # pass # move along, these aren't the drones you're looking for

    def addEvidence(self,dataX,dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        
        self.network = NeuralNetwork(inputLayer=dataX.shape[1],
                                     outputLayer=1,
                                     hiddenLayer=100)
##        training_data=zip(dataX,np.array(dataY))
        self.network.gradDescent(800000,
                                 dataX,
                                 dataY.values.reshape((dataX.shape[0],1)))
        
    def query(self,points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        points = points.values
        return self.network.forward(points)

if __name__=="__main__":
    print "the secret clue is 'zzyzx'"
