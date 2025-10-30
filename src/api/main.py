import os
from datetime import datetime

import joblib
import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
model = joblib.load("model.pkl")


class TextInput(BaseModel):
    text: str


DATABASE_URL = os.getenv("DATABASE_URL")


def log_prediction(text, sentiment):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            text TEXT,
            sentiment TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cur.execute(
        "INSERT INTO predictions (text, sentiment) VALUES (%s, %s)", (text, sentiment)
    )
    conn.commit()
    conn.close()


@app.post("/predict")
def predict(input: TextInput):
    prediction = model.predict([input.text])[0]
    log_prediction(input.text, prediction)
    return {"sentiment": prediction}


@app.get("/health")
def health():
    return {"status": "healthy"}
