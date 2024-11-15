from preprocessing import X_train_vec, X_test_vec, y_train, y_test, vectorizer
from knn import KNN
from naives_bayes import GaussianNaiveBayes
from sklearn.svm import SVC
from bagged_model import bagged_model
import os
import numpy as np

def assignment2():

    k = KNN()
    gnb = GaussianNaiveBayes()
    svc = SVC()

    k.fit(X_train_vec, y_train)
    gnb.fit(X_train_vec, y_train)
    svc.fit(X_train_vec, y_train)

    models = [k,gnb,svc]

    emails = []
    folder_path = 'test'

    emails = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
                email_content = file.read()
                emails.append(email_content)

    vector_emails = vectorizer.transform(emails).toarray()

    predictions = bagged_model(models,vector_emails)

    return np.array(predictions)
