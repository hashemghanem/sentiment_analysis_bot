import logging
import os
import time
from datetime import datetime

import joblib
import psycopg2
from fastapi import FastAPI
from opencensus.ext.azure import metrics_exporter
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
from pydantic import BaseModel

# Setup Application Insights
CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")

# Configure logging
logger = logging.getLogger(__name__)
if CONNECTION_STRING:
    logger.addHandler(AzureLogHandler(connection_string=CONNECTION_STRING))
    logger.setLevel(logging.INFO)

# Setup metrics
stats = stats_module.stats
view_manager = stats.view_manager

# Create measures
prediction_measure = measure_module.MeasureFloat(
    "prediction_latency", "Latency of prediction requests", "ms"
)

# Create views
prediction_view = view_module.View(
    "prediction_latency_view",
    "Latency of predictions",
    [],
    prediction_measure,
    aggregation_module.LastValueAggregation(),
)

view_manager.register_view(prediction_view)

# Create metrics exporter
if CONNECTION_STRING:
    exporter = metrics_exporter.new_metrics_exporter(
        connection_string=CONNECTION_STRING
    )
    view_manager.register_exporter(exporter)

app = FastAPI(title="ML Sentiment API")
model = joblib.load("model.pkl")

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            text TEXT,
            sentiment TEXT,
            confidence FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


def log_prediction(text, sentiment, confidence):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO predictions (text, sentiment, confidence) VALUES (%s, %s, %s)",
            (text, sentiment, confidence),
        )
        conn.commit()
        conn.close()
        logger.info(f"Prediction logged: {sentiment} ({confidence:.2f})")
    except Exception as e:
        logger.error(f"Failed to log prediction: {str(e)}")


class TextInput(BaseModel):
    text: str


@app.post("/predict")
def predict(input: TextInput):
    start_time = time.time()

    try:
        # Make prediction
        prediction = model.predict([input.text])[0]
        proba = model.predict_proba([input.text])[0]
        confidence = max(proba)

        # Log to database
        log_prediction(input.text, prediction, confidence)

        # Log to Application Insights
        latency_ms = (time.time() - start_time) * 1000

        mmap = stats.stats_recorder.new_measurement_map()
        tmap = tag_map_module.TagMap()
        mmap.measure_float_put(prediction_measure, latency_ms)
        mmap.record(tmap)

        logger.info(
            f"Prediction: {prediction}, Confidence: {confidence:.2f}, Latency: {latency_ms:.2f}ms"
        )

        return {
            "sentiment": prediction,
            "confidence": float(confidence),
            "latency_ms": latency_ms,
        }
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/metrics")
def metrics():
    """Prometheus-compatible metrics endpoint"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get prediction counts by sentiment
        cur.execute(
            """
            SELECT sentiment, COUNT(*) as count
            FROM predictions
            WHERE timestamp > NOW() - INTERVAL '1 hour'
            GROUP BY sentiment
        """
        )
        results = cur.fetchall()

        # Get average confidence
        cur.execute(
            """
            SELECT AVG(confidence) as avg_confidence
            FROM predictions
            WHERE timestamp > NOW() - INTERVAL '1 hour'
        """
        )
        avg_conf = cur.fetchone()[0] or 0

        conn.close()

        metrics_output = "# HELP predictions_total Total number of predictions\n"
        metrics_output += "# TYPE predictions_total counter\n"

        for sentiment, count in results:
            metrics_output += f'predictions_total{{sentiment="{sentiment}"}} {count}\n'

        metrics_output += "\n# HELP average_confidence Average prediction confidence\n"
        metrics_output += "# TYPE average_confidence gauge\n"
        metrics_output += f"average_confidence {avg_conf}\n"

        return metrics_output
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        return "# Error generating metrics\n"
