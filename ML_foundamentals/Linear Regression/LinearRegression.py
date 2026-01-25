import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import learning_curve

def evaluate(modelName, model, trainSet, testSet):
    X_train, y_train = trainSet
    X_test, y_test = testSet
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    print(f"Evaluation of {modelName} on trainSet:")
    print(f"MSE: {mean_squared_error(y_train, train_pred)}\nMAE: {mean_absolute_error(y_train, train_pred)}\nR2: {r2_score(y_train, train_pred)}")
    print(f"\nEvaluation of {modelName} on testSet:")
    print(f"MSE: {mean_squared_error(y_test, test_pred)}\nMAE: {mean_absolute_error(y_test, test_pred)}\nR2: {r2_score(y_test, test_pred)}")
    #print(f"Weights: {model.coef_}\nBias: {model.intercept_}")
    print("-------------------------------------------------")


dataSet = pd.read_csv('data/boston.csv')
dataSet = dataSet.drop(dataSet.columns[0], axis=1)

correlation_matrix = dataSet.corr()

#sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
#plt.title('Correlation Matrix Heatmap')
#plt.tight_layout()
#plt.show()


scaler = StandardScaler()
poly = PolynomialFeatures()


#DATA PREPROCESSING

#First step, split the dataset between features and target 
X = dataSet.drop("PRICE", axis= 1).values #extract features
Y = dataSet["PRICE"].values #extract traget

#Second step split the features set into training set and testing set
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=0)

#Third step create polinomial features (optional)
X_train = poly.fit_transform(X_train)
X_test = poly.transform(X_test)

#Fourth step normalization
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

#END OF DATA PREPROCESSING

#MODELS TRAINING AND EVALUATION

#Linear Regression with feature scaling (normalized) using all the features to predict the target
ll_scaled = LinearRegression()
ll_scaled.fit(X_train, Y_train.reshape(-1, 1))
Y_pred_scaled = ll_scaled.predict(X_test)
evaluate("Scaled Linear Regression" , ll_scaled, (X_train, Y_train), (X_test, Y_test))

#Ridge Regression (L1)
ridge_model = Ridge(alpha=1.)

ridge_model.fit(X_train, Y_train)
evaluate("Ridge Regression", ridge_model, (X_train, Y_train), (X_test, Y_test))

#Lasso Regression (L2)
lasso_model = Lasso(alpha=1.)

lasso_model.fit(X_train, Y_train)
evaluate("Lasso Regression", lasso_model, (X_train, Y_train), (X_test, Y_test))

#ElasticNet (L1+L2)
elastic_model = ElasticNet(alpha=1. , l1_ratio=0.5)

elastic_model.fit(X_train, Y_train)
evaluate("ElasticNet", elastic_model, (X_train, Y_train), (X_test, Y_test))



#Let's find best lambda value for Ridge

def evaluate_ridge(model, trainSet, testSet):
    X_train, Y_train = trainSet
    X_test, Y_test = testSet
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    R2_train = r2_score(Y_train, y_train_pred)
    R2_test = r2_score(Y_test, y_test_pred)
    return (1-R2_train/R2_test)
    

alphas = [0.00001, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
best_model = None
best_eval = None
best_alpha = None

for alpha in alphas:
    model = Ridge(alpha=alpha)

    model.fit(X_train, Y_train)
    evaluation = evaluate_ridge(model, (X_train, Y_train), (X_test, Y_test))
    if best_eval is None or best_eval < evaluation:
        best_eval = evaluation
        best_model = model
        best_alpha = alpha

print(f"Best Ridge model found with alpha = {best_alpha}.")
evaluate("Best Ridge Model", best_model, (X_train, Y_train), (X_test, Y_test))

#Lets show the learning curve
sns.set_theme()
train_size_abs, train_scores, test_scors = learning_curve(
    Ridge(alpha=10),
    X,
    Y,
    random_state=0
)
plt.plot(train_size_abs, train_scores.mean(axis=1), label='Train Score')
plt.plot(train_size_abs, test_scors.mean(axis=1), label='Test Score')
plt.legend()
plt.show()