import numpy as np

class KNN:
    def __init__(self,k=3):
        self.k = k

    def fit(self,X,y):
        self.X_train = X 
        self.y_train = y 

    def predict(self,X):
        predictions = []
        for x in X:
            predictions.append(self._predict(x))
        return predictions
    
    def _predict(self,x):
        # Compute distances
        distances = np.linalg.norm(self.X_train - x , axis =1)

        # Calculate top k nearest neighbour
        top_k_idx = np.argsort(distances)[:self.k]

        # Choose maximum element
        cnt_0 = 0
        cnt_1 = 0

        for k in top_k_idx:
            if self.y_train[k] == 1:
                cnt_1 += 1
            else:
                cnt_0 += 1
        
        if cnt_0 > cnt_1:
            return 0
        return 1