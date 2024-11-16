import numpy as np
import matplotlib.pyplot as plt

class PCA:

    def __init__(self):
        self.mean = None
        self.eigenVectors = None
        self.eigenValues = None

    def fit(self, X):

        # Center the dataset
        self.mean = X.mean(axis=0)
        X = X - self.mean

        # Compute Covariance matrix
        cov = np.cov(X.T)

        # find eigen values and vectors
        values,vectors = np.linalg.eigh(cov)
        vectors = vectors.T

        # sort them
        idxs = np.argsort(values)[::-1]
        values = values[idxs]
        vectors = vectors[idxs]

        self.eigenValues = values
        self.eigenVectors = vectors


    def transform(self,X,n_components):

        # center the dataset
        X = X - self.mean

        # compute projected X

        projectedX = X @ self.eigenVectors[:n_components].T

        # return projected X
        return projectedX


    def variance_ratio(self,pc):
        var = self.eigenValues[pc] / sum(self.eigenValues) * 100
        return var.round(2)

    def inverse_transform(self,X):
        # get the reduced dimension of data
        dimension = X.shape[0]

        # Compute eigenvector.T @ transformed data
        reconstructed = self.eigenVectors[:dimension].T @ X

        # Add mean to it
        reconstructed += self.mean

        # Return reconstructed image
        return reconstructed
    

def plot_images(pca,imagesArray,idx):
    plt.figure(figsize=(14, 7))
    plt.suptitle(f"1.b) Image Reconstruction for {idx//100}", fontsize=26)

    plt.subplot(2,4,1)
    plt.imshow(imagesArray[idx].reshape(28,28))
    plt.title('Original Image')

    for pc in range(50,701,100):
        plt.subplot(2,4, (pc//100)+2)

        reducedImage = pca.transform(imagesArray[idx],pc)
        reconstructed = pca.inverse_transform(reducedImage)

        plt.imshow(reconstructed.reshape(28,28))
        plt.axis('off')
        plt.title(f"{pc} principal component")

    plt.show()

