from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np


app = FastAPI()

def train_model(X, y):
    model = LinearRegression()
    model.fit(X, y)

    return model

def make_predictions(model, X):
    return model.predict(X)

class TrainingData(BaseModel):
    X: list[float]
    y: list[float]

@app.post("/training")
async def train(data: TrainingData):
    X = [[array] for array in np.array(data.X)]
    y = np.array(data.y)

    model = train_model(X, y)
    print(model)

    predictions = make_predictions(model, X)
    print(predictions)

    mse = mean_squared_error(y, predictions)
    print(mse)

    return {"mse": mse}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0.", port=8000)