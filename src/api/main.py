import joblib
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
model = joblib.load("model.pkl")


class TextInput(BaseModel):
    text: str


@app.post("/predict")
def predict(input: TextInput):
    prediction = model.predict([input.text])[0]
    return {"sentiment": prediction}


@app.get("/health")
def health():
    return {"status": "healthy"}
