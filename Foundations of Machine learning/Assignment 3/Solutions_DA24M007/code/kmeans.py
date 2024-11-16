import numpy as np
import matplotlib.pyplot as plt


class KmeansClustering:
    
    def __init__(self,k=2,max_iter = 10, seed = 42):
        # number of clusters is represented by k
        self.k = k
        # max_iter -  maximum number of iterations to stop, if the algo did not converge 
        self.max_iter = max_iter
        # initilaising centroids
        self.centroids = [None] * k
        # setting random seed to determine initlisation
        np.random.seed(seed)
        # errors, to store the error history across iterations
        self.errors=[]

    def fit(self,X):
        # choosing random points as centroids
        random_idx = np.random.choice(len(X), self.k,replace=False)
        self.centroids = X[random_idx]

        for _ in range(self.max_iter):
            # compute distance for every point to every cluster
            distances = np.linalg.norm(X[:,np.newaxis] - self.centroids , axis = 2)
            # choose the centroid with minimum distance
            labels = np.argmin(distances,axis=1)

            # update centroids by calculating the mean of cluster
            new_centroids = []
            for i in range(self.k):
                new_centroids.append(X[labels == i].mean(axis=0))

            new_centroids = np.array(new_centroids)

            # compute error as the squared distance between data points and its cluster centroid
            error = np.sum((X - self.centroids[labels]) ** 2)
            self.errors.append(error)

            # If the centroids are not updating (reached convergence), stop the algorithm
            if np.allclose(self.centroids, new_centroids):
                break
            self.centroids = new_centroids


    def predict(self,X):
        # compute the distance of test point with the final cluster centroids
        distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)

        # choose the cluster with minimum distance fro centroids
        labels = np.argmin(distances, axis=1)

        # Return the label of that cluster
        return labels
    

def plot_voronoi(X, kmeans, k):
    grid_shape = (100, 150) 
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, grid_shape[0]),
                         np.linspace(y_min, y_max, grid_shape[1]))
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    
    labels_grid = kmeans.predict(grid_points)
    
    Z = labels_grid.reshape(xx.shape)
    
    cmap = plt.cm.Paired 
    
    plt.figure(figsize=(8, 6))
    plt.contourf(xx, yy, Z, cmap=cmap, alpha=0.2)  
    
    labels = kmeans.predict(X)
    for cluster_id in range(k):
        cluster_points = X[labels == cluster_id]
        plt.scatter(cluster_points[:, 0], cluster_points[:, 1], 
                    label=f'Cluster {cluster_id+1}', 
                    color=cmap(cluster_id / k), alpha=1) 
    
        plt.scatter(kmeans.centroids[:, 0], kmeans.centroids[:, 1], 
                color='red', marker='x', s=100, label='Cluster Centers')
    
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.title(f'Voronoi Regions for K={k}')
    plt.legend()
    plt.show()