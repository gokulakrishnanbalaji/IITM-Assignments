import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



def crossValidation(parameters,model,X,y,title=None,x_axis=None,y_axis=None):
    best_parameter = parameters[0]
    best_error = float('inf')
    error_history=[]

    np.random.seed(10)
    test_indices = np.random.choice(X.shape[0] , int(X.shape[0]/4) , replace=False)
    train_indices = [i for i in range(X.shape[0]) if i not in test_indices ]

    X_train = pd.DataFrame(X.to_numpy()[train_indices])
    y_train = y.to_numpy()[train_indices]

    X_test = pd.DataFrame(X.to_numpy()[test_indices])
    y_test = y.to_numpy()[test_indices]

    for p in parameters:
        m = model(p)
        m.fit(X_train, y_train)
        
        curr_error = m.error(X_test,y_test)

        if curr_error < best_error:
            best_error = curr_error
            best_parameter = p 

        error_history.append(curr_error)

    plt.plot(parameters, error_history)
    plt.title(title)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.show()

    return best_parameter


        
        
