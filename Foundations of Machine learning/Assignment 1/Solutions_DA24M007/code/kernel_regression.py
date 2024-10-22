import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class KernelRegression:
    def __init__(self, sigma=1):
        self.sigma = sigma
        self.alpha = []
        self.X_train=[]

    def _compute(self,u,v):
        numerator = (np.linalg.norm(u-v)) ** 2
        denominator = -2 * self.sigma**2
        
        return np.exp(numerator / denominator)
    
    def fit(self,X,y):
        X=X.to_numpy()
        n,d = X.shape
        self.X_train = X

        k = np.zeros((n,n))
        

        for i in range(n):
            for j in range(n):
                k[i,j] = self._compute(X[i] , X[j])

        self.alpha = np.linalg.solve(k,y)

    def predict(self,X_test):
        X_test=X_test.to_numpy()
        y_pred = []
        for x in X_test:
            k_test = []

            for i in self.X_train:
                k_test.append(self._compute(x,i))

            k_test = np.array(k_test)

            y_pred.append(self.alpha @ k_test)

        return np.array(y_pred)
    
    def error(self,X_test, y_test):

        y_pred = self.predict(X_test)
        return np.round(np.sum((y_pred - y_test) **2 ) / X_test.shape[0], 2)

