import numpy as np
import pandas as pd

class Volatility(object):
    def __init__(self, window=20):
        self.window = window
        self.name = "Volatility_{}".format(window)

    def addEvidence(self, data):
        self.data = data

    def getIndicator(self):
    	returns = self.data/self.data.shift(1) - 1
        vol = pd.rolling_std(returns, self.window) * np.sqrt(252)

        vol.columns = [self.name+"_"+x for x in vol.columns]

        return vol
