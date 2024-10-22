import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt

plt.figure(figsize=(6, 6))

#Loading dataset
#Make sure the dataset.cv is in the same folder as main.py
df = pd.read_csv('dataset.csv')
df.columns = ['X','Y']

#Plotting the original image
plt.scatter(df.X,df.Y)
plt.title('original plotted image')
plt.show()

#Rounding off the decimal values to near integer and saving it
df['X'] = df['X'].round().astype(int)
df['Y'] = df['Y'].round().astype(int)

plt.scatter(df.X,df.Y)
plt.title('Rounded(int) plotted image')
plt.show()

#Converting the df into numpy matrix
mat = np.zeros((100, 100))

for x, y in zip(df['X'], df['Y']):
    mat[x][y]=1

#Rotating the matrix by 90 degrees 
tmp = np.zeros((100,100))
for i in range(100):
    tmp[100-i-1][i]=1
matT = np.transpose(mat)
mat_1  = np.matmul(matT,tmp)

#Constructing df_1 from mat_1
indices_1 = np.argwhere(mat_1 == 1)
df_1 = pd.DataFrame(indices_1, columns=['X', 'Y'])

#Saving img_1
plt.scatter(df_1.X,df_1.Y)
plt.title('Rotated by 90 degrees')
plt.show()

#Flipping the matrix horizontally 
tmp = np.zeros((100,100))
for i in range(100):
    tmp[100-i-1][i]=1
mat_2  = np.matmul(mat,tmp)
    
#Constructing df_2 from mat_2
indices_2 = np.argwhere(mat_2 == 1)
df_2 = pd.DataFrame(indices_2, columns=['X', 'Y'])

#Plotting img_2
plt.scatter(df_2.X,df_2.Y)
plt.title('Horizontally flipped image')
plt.show()
