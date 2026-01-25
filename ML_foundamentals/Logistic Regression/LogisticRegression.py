import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, classification_report, RocCurveDisplay
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import learning_curve
from sklearn.datasets import make_classification

def plt_decision_boundary(model, dataset):
    X, y = dataset
    h = 0.02

    x_min, x_max = X[:,0].min()-1, X[:,0].max()+.1
    y_min, y_max = X[:,1].min()-1, X[:,1].max()+.1

    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    plt.contourf(xx, yy , Z, cmap= plt.cm.Paired)

    plt.scatter(X[:, 0], X[:, 1], c = y, edgecolor='white')
    plt.show()

X, y = make_classification(n_samples=100, 
                           n_features=2, 
                           n_informative=2, 
                           n_redundant=0, 
                           n_repeated=0,
                           n_classes=2,
                           random_state=0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.3)

lr = LogisticRegression()

lr.fit(X_train, y_train)

#plt_decision_boundary(lr, (X_test, y_test))

y_proba_train = lr.predict_proba(X_train)
y_proba_test = lr.predict_proba(X_test)

test_loss = log_loss(y_test, y_proba_test)
train_loss = log_loss(y_train, y_proba_train)

print(f"test_loss: {test_loss}\ntrain_loss: {train_loss}")

y_pred_train = lr.predict(X_train)
y_pred_test = lr.predict(X_test)
cm = confusion_matrix(y_train, y_pred_train)

def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    df_cm = pd.DataFrame(cm, 
                         index=["Negative", "Positive"],
                         columns=["Predicted Negative","Predicted Positive"])
    sns.heatmap(df_cm, annot=True, cmap='Blues')
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.show()
    sns.s

#plot_confusion_matrix(y_train, y_pred_train)
print(classification_report(y_test, y_pred_test))
print(classification_report(y_train, y_pred_train))
RocCurveDisplay.from_estimator(lr, X_test, y_test)
plt.show()