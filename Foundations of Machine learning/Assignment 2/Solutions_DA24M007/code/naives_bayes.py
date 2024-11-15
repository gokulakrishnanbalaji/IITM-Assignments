import numpy as np

class GaussianNaiveBayes:
    def fit(self, X, y):
        self.classes = np.unique(y)
        self.mean = {}
        self.variance = {}
        self.prior = {}
        self.smoothing = 1e-9

        for cls in self.classes:
            X_cls = X[y == cls]
            self.mean[cls] = np.mean(X_cls, axis=0)
            self.variance[cls] = np.var(X_cls, axis=0) + self.smoothing
            self.prior[cls] = np.log(X_cls.shape[0] / X.shape[0])  # Log prior

    def gaussian_probability(self, x, mean, var):
        exponent = - ((x - mean) ** 2) / (2 * var)
        return np.log(1 / np.sqrt(2 * np.pi * var)) + exponent  # Log probability

    def predict(self, X):
        predictions = []
        for x in X:
            class_probabilities = {}
            for cls in self.classes:
                likelihood = self.gaussian_probability(x, self.mean[cls], self.variance[cls])
                class_probabilities[cls] = self.prior[cls] + np.sum(likelihood)  # Log sum
            predictions.append(max(class_probabilities, key=class_probabilities.get))
        return np.array(predictions)