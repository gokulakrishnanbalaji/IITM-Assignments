from preprocessing import X_train_vec, X_test_vec, y_train, y_test, vectorizer
from knn import KNN
from naives_bayes import GaussianNaiveBayes
from sklearn.svm import SVC
from bagged_model import bagged_model
from sklearn.metrics import classification_report

k = KNN()
gnb = GaussianNaiveBayes()
svc = SVC()

k.fit(X_train_vec, y_train)
gnb.fit(X_train_vec, y_train)
svc.fit(X_train_vec, y_train)

y_pred = bagged_model([k,gnb,svc], X_test_vec)

print(classification_report(y_test, y_pred))