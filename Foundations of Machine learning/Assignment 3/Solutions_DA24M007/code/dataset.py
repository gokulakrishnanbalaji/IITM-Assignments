import numpy as np
import pandas as pd
from datasets import load_dataset

# --------------- Loading dataset for PCA ---------------

ds = load_dataset("ylecun/mnist")

images = {}
cnt = [0] * 10
for i in range(10):
    images[i]=[]

for i in ds['train']:
    if cnt[i['label']] < 100:
        images[i['label']].append(i['image'])
        cnt[i['label']] += 1

imagesArray = []
for i in images:
    for j in images[i]:
        imagesArray.append(np.array(j).flatten())

imagesArray = np.array(imagesArray)


# --------------- Loading dataset for Kmeans Clustering ---------------
df = pd.read_csv('cm_dataset_2.csv',header=None)
df.columns = ['x1','x2']

X_kmeans = df.to_numpy()