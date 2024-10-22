import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from gradient_descent import GradientDescent

class MLE_Regression():
    def __init__(self,lr=0.001):
        self.lr = lr
        self.w = []

    def fit(self,X,y):
        X=X.copy()
        n,d = X.shape
        X['bias'] = np.ones(n)
        d+=1 

        # w = (X.t X) ^(-1) X.T y
        self.w = np.array(np.linalg.inv(X.T @ X) @ X.T @ y )


    def predict(self,X):
        X=X.copy()
        X['bias'] = np.ones(X.shape[0])

        return X @ self.w
    
    def error(self,X_test, y_test):
        X_test=X_test.copy()
        X_test['bias'] = np.ones(X_test.shape[0])
        y_pred = X_test @ self.w

        return np.round(np.sum((y_pred - y_test) **2 ) / X_test.shape[0], 2)






    
