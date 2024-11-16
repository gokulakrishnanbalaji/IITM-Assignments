import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

from pca import PCA, plot_images
from dataset import imagesArray, X_kmeans
from kmeans import KmeansClustering, plot_voronoi
# 1.a) Visualise top principal components and print their explained variance
pca = PCA()
pca.fit(imagesArray)

top_10_eigenvectors = pca.eigenVectors[:10]

plt.figure(figsize=(12, 6))

for i in range(10):
    plt.subplot(2, 5, i+1)
    plt.plot(top_10_eigenvectors[i])
    plt.title(f'PC {i+1}')
    plt.xlabel('Feature Index')
    plt.ylabel('Eigenvector Value')

plt.suptitle('1.a) First 10 Principal Components', fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 
plt.show()

print('Explained variance ratio')
for i in range(10):
    print(f"Principal component {i+1} - {pca.variance_ratio(i)} %")


# 1.b) Reconstructing image using principal components
plot_images(pca,imagesArray, 3) # (3//100 = 0), we are using image with label 0
plot_images(pca,imagesArray, 403) # (403//100 = 4), we are using image with label 4

# 2. Kmeans Clustering

# 2.a) Lloyd's Algo with k as 2 but with different initialisations

for i in range(5):
    kmeans = KmeansClustering(k=2, seed=i)
    kmeans.fit(X_kmeans)
    labels= kmeans.predict(X_kmeans)
    
   
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(kmeans.errors, marker='o')
    plt.title(f'Initialization {i+1}: Error over Iterations')
    plt.xlabel('Iterations')
    plt.ylabel('Error')

    plt.subplot(1, 2, 2)

    for cluster_id in range(kmeans.k): 
        cluster_points = X_kmeans[labels == cluster_id]
        plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=f'Cluster {cluster_id+1}')
    
    plt.scatter(kmeans.centroids[:, 0], kmeans.centroids[:, 1], color='black', marker='x', s=100, label='Centroids')
    plt.title(f'Initialization {i+1}: Clusters')
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.legend()
    plt.show()

# 2.b) Printing vornoi regions for k = 2,3,4,5 with same initialisation.

for k in range(2, 6, 1):
    kmeans = KmeansClustering(k=k) 
    kmeans.fit(X_kmeans)

    plot_voronoi(X_kmeans, kmeans, k)