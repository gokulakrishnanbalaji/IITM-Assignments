import numpy as np

class StochasticGRadientDescent:
    def __init__(self,batch_size = 100, lr = 0.1, max_iter=250):
        self.batch_size = batch_size
        self.lr = lr
        self.max_iter = max_iter
        self.w = []
        self.w_history=[]

    def fit(self,X,y):
        X=X.copy()
        n,d = X.shape
        X['bias']=np.ones(n)
        d+=1
        self.w = np.random.randn(d)

        for _ in range(self.max_iter):
            indices = np.random.choice(n,self.batch_size,replace=False)
            xi = X.to_numpy()[indices]
            yi = y.to_numpy()[indices]
            
            dw = (2/self.batch_size) * (xi @ self.w - yi) @ xi
            self.w -= self.lr * dw

            self.w_history.append(self.w.copy())

        
        avg_w = [0,0,0]
        for w in self.w_history:
            for i in range(3):
                avg_w[i] += w[i]

        for i in range(3):
            avg_w[i] = avg_w[i] / len(self.w_history)
        self.w = np.array(avg_w)
        

    def predict(self,X):
        X=X.copy()
        X['bias'] = np.ones(X.shape[0])

        return X @ self.w
    
    def error(self,X_test, y_test):
        X_test=X_test.copy()
        X_test['bias'] = np.ones(X_test.shape[0])
        
        y_pred = X_test @ self.w
        return np.round(np.sum((y_pred - y_test) **2 ) / X_test.shape[0], 2)

    