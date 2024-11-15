import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

df = pd.read_csv('email.csv')

df['Category'] = df['Category'].map({'ham': 0, 'spam': 1})

X_train, X_test, y_train, y_test = train_test_split(df['Message'], df['Category'], test_size=0.3, random_state=42)

vectorizer = TfidfVectorizer(max_features=500)

X_train_vec = vectorizer.fit_transform(X_train).toarray()
X_test_vec = vectorizer.transform(X_test).toarray()

y_train = y_train.to_numpy()
y_test = y_test.to_numpy()
