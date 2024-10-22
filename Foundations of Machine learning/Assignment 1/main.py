# Importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Importing machine learning algorithms implemented without using sklearn functions
from mle import MLE_Regression
from gradient_descent import GradientDescent
from stochastic_gd import StochasticGRadientDescent
from ridge_regression import RidgeRegression
from cross_validation import crossValidation
from kernel_regression import KernelRegression

# Preparing data required for training and testing
df_train = pd.read_csv('FMLA1Q1Data_train.csv',header = None)
df_test = pd.read_csv('FMLA1Q1Data_test.csv',header = None)
cols = ['x1','x2','y']
df_train.columns = cols
df_test.columns = cols

X_train = df_train.drop('y',axis=1)
y_train = df_train.y

X_test = df_test.drop('y',axis=1)
y_test = df_test.y



print('---------------------- Question 1 ---------------------------')
# Calculate w_ml from using closed form solution 

mle = MLE_Regression()
mle.fit(X_train, y_train)
print(f"w_ml : {mle.w}")


print('---------------------- Question 2 ---------------------------')
# compute w_gd using gradient descent algorithm and to compare its value with w_ml for every iteration

gd = GradientDescent()
gd.fit(X_train,y_train)
print(f"w_gd : {gd.w.to_numpy()}")

difference = []
for i in range(gd.max_iter):
    diff = np.sum((gd.w_history[i] - mle.w) ** 2)
    difference.append(float(diff))

plt.plot(difference)
plt.title('Comparison of weight from gradient descent at various iterations with weight from analytical solution')
plt.xlabel('Iterations')
plt.ylabel('|| w_gd_t - w_ml|| ^ 2')
plt.show()

print('---------------------- Question 3 ---------------------------')
# compute w using stochastic gradient descent with batch size 100 and to compare its value with w_ml for every iteration

sgd = StochasticGRadientDescent(batch_size=100)
sgd.fit(X_train,y_train)
print(f"w_sgd : {sgd.w}")

difference = []
for i in range(sgd.max_iter):
    diff = np.sum((sgd.w_history[i] - mle.w) ** 2)
    difference.append(float(diff))

plt.plot(difference)
plt.title('Comparison of weight from stochastic gradient descent with batch size 100 at various iterations with weight from analytical solution')
plt.xlabel('Iterations')
plt.ylabel('|| w_sgd_t - w_ml|| ^ 2')
plt.show()


print('---------------------- Question 4 ---------------------------')
# Cross validate various values of lambda in the ridge regression and find the optimal weight

lambda_values = [0.01,0.1,1,2,3,6,10]
best_lambda = crossValidation(lambda_values, RidgeRegression, X_train, y_train,title = 'Validation error for various lamdas in ridge regression' ,x_axis='Lambda values' , y_axis='Mean squared error')
print(f"Best lambda with least error on validation set: {best_lambda}")
rr = RidgeRegression(l=1)
rr.fit(X_train,y_train)
print(f'w_r with lambda {best_lambda} = {rr.w.to_numpy()}')

# Comparing errors by w_r and w_ml on test data
ml_error = mle.error(X_test,y_test)
r_error = rr.error(X_test,y_test)
print(f'Error on test sets : ')
print(f"                    with w_ml: {ml_error}")
print(f"                    with w_ridge: {r_error}")


print('---------------------- Question 5 ---------------------------')
# perform cross validation for kernel regression on sigma(standard deviation of the gaussian kernel)

sigma_values = np.arange(1,10,1)
best_sigma = crossValidation(sigma_values, KernelRegression, X_train, y_train, title='Validation error for various sigma in gaussian kernel', x_axis='sigma values',y_axis='validation error')
print(f"Best sigma for gaussain kernel: {best_sigma}")
kr = KernelRegression(sigma=best_sigma)
kr.fit(X_train,y_train)
kernel_error = kr.error(X_test,y_test)

print(f'Error on test sets : ')
print(f"                    with w_ml: {ml_error}")
print(f"                    with gaussian kernel: {kernel_error}")

# Comparing performance of kernel regression with closed form solution
plt.scatter(np.arange(y_test.shape[0]),y_test.to_numpy(), color = 'red', label='Original')
plt.scatter(np.arange(y_test.shape[0]),mle.predict(X_test), color = 'green', label = 'MLE')
plt.scatter(np.arange(y_test.shape[0]),kr.predict(X_test), color = 'blue',label='Kernel')
plt.title('predicted points by Analytical solution and kernel regression')
plt.xlabel('Data Points index')
plt.ylabel('Actual Value of points')
plt.legend()
plt.show()

# Plotting the error values of our function with test data 

model_names = {'Analytical': ml_error,
               'Gradient descent': gd.error(X_test,y_test),
                 'SGD':sgd.error(X_test,y_test) , 
                 'Ridge': r_error ,
                 'Kernel': kernel_error
                 }

print('-------------------------------------')
print('Error of various models on test data')
for i in model_names:
    print(f"{i} : {model_names[i]}")

plt.scatter(model_names.keys(), model_names.values())
plt.title('Error of various models on test data')
plt.xlabel('Model Names')
plt.ylabel('Mean Squared Error')
plt.show()