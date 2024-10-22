import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt

class GradientDescent():
    def __init__(self,lr=0.001,max_iter=1000):
        self.lr = lr 
        self.max_iter = max_iter
        self.w = []
        self.w_history = []

    def fit(self,X,y):
        X=X.copy()
        n,d = X.shape
        d+=1
        X['bias'] = np.ones(n)
        self.w=np.zeros(d)
        
        for _ in range(self.max_iter):

            dw = (2/n) * (X @ self.w  - y) @ X 
            self.w -= self.lr * dw

            self.w_history.append(self.w.copy())


    def predict(self,X):
        X=X.copy()
        X['bias'] = np.ones(X.shape[0])

        return X @ self.w
    
    def error(self,X_test, y_test):
        X_test=X_test.copy()
        X_test['bias'] = np.ones(X_test.shape[0])
        
        y_pred = X_test @ self.w
        return np.round(np.sum((y_pred - y_test) **2 ) / X_test.shape[0], 2)
