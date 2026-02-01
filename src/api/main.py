import logging
import os
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime

import joblib
import psycopg2
from fastapi import FastAPI, Response
from psycopg2 import pool
from pydantic import BaseModel

# Setup Application Insights with Azure Monitor OpenTelemetry
CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")

# Configure logging - ensure logs go to stdout AND Application Insights
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Always add stdout handler for container logging (kubectl logs)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(stream_handler)

# Configure Azure Monitor OpenTelemetry
if CONNECTION_STRING:
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        from opentelemetry import trace
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        # Configure Azure Monitor with the connection string
        configure_azure_monitor(
            connection_string=CONNECTION_STRING,
            enable_live_metrics=True,
        )

        # Get tracer for custom spans
        tracer = trace.get_tracer(__name__)

        logger.info("Azure Monitor OpenTelemetry configured successfully")
        TELEMETRY_ENABLED = True
    except Exception as e:
        logger.warning(f"Failed to configure Azure Monitor OpenTelemetry: {e}")
        tracer = None
        TELEMETRY_ENABLED = False
else:
    logger.warning("APPLICATIONINSIGHTS_CONNECTION_STRING not set - telemetry disabled")
    tracer = None
    TELEMETRY_ENABLED = False

app = FastAPI(title="ML Sentiment API")

# Instrument FastAPI with OpenTelemetry (after app creation)
if TELEMETRY_ENABLED:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to instrument FastAPI: {e}")

model = joblib.load("model.pkl")

DATABASE_URL = os.getenv("DATABASE_URL")

# ============================================================
# DATABASE CONNECTION POOLING WITH GRACEFUL STARTUP
# ============================================================


class DatabasePool:
    """
    Manages a connection pool with graceful startup.
    If the database is unavailable at startup, the application continues
    running and retries the connection in the background.
    """

    def __init__(self, database_url: str, minconn: int = 2, maxconn: int = 10):
        self.database_url = database_url
        self.minconn = minconn
        self.maxconn = maxconn
        self._pool = None
        self._lock = threading.Lock()
        self._initialized = False
        self._init_attempted = False

    def _create_pool(self) -> bool:
        """Attempt to create the connection pool. Returns True on success."""
        try:
            self._pool = pool.ThreadedConnectionPool(
                self.minconn, self.maxconn, self.database_url
            )
            self._initialized = True
            logger.info("Database connection pool created successfully")
            return True
        except Exception as e:
            logger.warning(f"Failed to create connection pool: {str(e)}")
            self._pool = None
            self._initialized = False
            return False

    def initialize(self):
        """
        Initialize the connection pool.
        Called at startup - does not crash if database is unavailable.
        """
        with self._lock:
            if self._init_attempted:
                return self._initialized
            self._init_attempted = True

        if self.database_url:
            success = self._create_pool()
            if not success:
                logger.warning(
                    "Database unavailable at startup. Will retry on first request."
                )
                # Start background retry thread
                retry_thread = threading.Thread(
                    target=self._background_retry, daemon=True
                )
                retry_thread.start()
        else:
            logger.warning("DATABASE_URL not configured")

        return self._initialized

    def _background_retry(self):
        """Background thread to retry database connection."""
        retry_count = 0
        max_retries = 10
        retry_delay = 5  # seconds

        while not self._initialized and retry_count < max_retries:
            time.sleep(retry_delay)
            retry_count += 1
            logger.info(
                f"Retrying database connection (attempt {retry_count}/{max_retries})"
            )

            with self._lock:
                if self._create_pool():
                    self._init_table()
                    return

        if not self._initialized:
            logger.error(f"Failed to connect to database after {max_retries} attempts")

    def _init_table(self):
        """Initialize the predictions table."""
        try:
            conn = self.get_connection()
            if conn:
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
                self.return_connection(conn)
                logger.info("Predictions table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize table: {str(e)}")

    def get_connection(self):
        """
        Get a connection from the pool.
        Returns None if pool is not available (graceful degradation).
        """
        # Try to initialize if not already done
        if not self._initialized and not self._init_attempted:
            self.initialize()

        # Retry initialization if previous attempt failed
        if not self._initialized:
            with self._lock:
                if not self._initialized and self.database_url:
                    if self._create_pool():
                        self._init_table()

        if self._pool and self._initialized:
            try:
                return self._pool.getconn()
            except Exception as e:
                logger.error(f"Failed to get connection from pool: {str(e)}")
                return None
        return None

    def return_connection(self, conn):
        """Return a connection to the pool."""
        if self._pool and conn:
            try:
                self._pool.putconn(conn)
            except Exception as e:
                logger.error(f"Failed to return connection to pool: {str(e)}")

    def is_ready(self) -> bool:
        """Check if database is ready (for readiness probe)."""
        if not self._initialized:
            return False

        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.fetchone()
                self.return_connection(conn)
                return True
            except Exception:
                self.return_connection(conn)
                return False
        return False

    def close(self):
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("Database connection pool closed")


# Initialize database pool (graceful startup - won't crash if DB is down)
db_pool = DatabasePool(DATABASE_URL)
db_pool.initialize()


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = db_pool.get_connection()
    try:
        yield conn
    finally:
        if conn:
            db_pool.return_connection(conn)


# ============================================================
# PREDICTION LOGGING WITH ERROR ISOLATION
# ============================================================


def log_prediction(text: str, sentiment: str, confidence: float):
    """
    Log prediction to database with error isolation.
    If database is unavailable, the error is logged but does not
    affect the prediction response.
    """
    try:
        with get_db_connection() as conn:
            if conn is None:
                logger.warning("Database unavailable - prediction not logged")
                return False

            cur = conn.cursor()
            cur.execute(
                "INSERT INTO predictions (text, sentiment, confidence) VALUES (%s, %s, %s)",
                (text, sentiment, confidence),
            )
            conn.commit()
            logger.info(f"Prediction logged: {sentiment} ({confidence:.2f})")
            return True
    except Exception as e:
        logger.error(f"Failed to log prediction: {str(e)}")
        return False


# ============================================================
# API ENDPOINTS
# ============================================================


class TextInput(BaseModel):
    text: str


@app.post("/predict")
def predict(input: TextInput):
    """
    Make a sentiment prediction.
    Predictions succeed even if database logging fails (error isolation).
    """
    start_time = time.time()

    # Make prediction (core functionality - always works)
    prediction = model.predict([input.text])[0]
    proba = model.predict_proba([input.text])[0]
    confidence = max(proba)

    # Log to database (non-blocking - failures don't affect response)
    log_prediction(input.text, prediction, confidence)

    # Calculate latency
    latency_ms = (time.time() - start_time) * 1000

    # Log with OpenTelemetry tracing
    if tracer:
        with tracer.start_as_current_span("prediction_metrics") as span:
            span.set_attribute("prediction.sentiment", prediction)
            span.set_attribute("prediction.confidence", float(confidence))
            span.set_attribute("prediction.latency_ms", latency_ms)
            span.set_attribute("prediction.text_length", len(input.text))

    logger.info(
        f"Prediction: {prediction}, Confidence: {confidence:.2f}, Latency: {latency_ms:.2f}ms"
    )

    return {
        "sentiment": prediction,
        "confidence": float(confidence),
        "latency_ms": latency_ms,
    }


@app.get("/health")
def health():
    """
    Liveness probe - checks if the application is running.
    Returns healthy as long as the API can respond.
    Does NOT check database (use /ready for that).
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/ready")
def ready(response: Response):
    """
    Readiness probe - checks if the application is ready to serve traffic.
    Verifies database connectivity and model availability.
    """
    checks = {"model": False, "database": False}

    # Check model is loaded
    try:
        checks["model"] = model is not None
    except Exception:
        checks["model"] = False

    # Check database connectivity
    checks["database"] = db_pool.is_ready()

    all_ready = all(checks.values())

    if not all_ready:
        response.status_code = 503
        return {
            "status": "not_ready",
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
        }

    return {
        "status": "ready",
        "checks": checks,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/metrics")
def metrics():
    """Prometheus-compatible metrics endpoint"""
    try:
        with get_db_connection() as conn:
            if conn is None:
                return "# Database unavailable\n"

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

            metrics_output = "# HELP predictions_total Total number of predictions\n"
            metrics_output += "# TYPE predictions_total counter\n"

            for sentiment, count in results:
                metrics_output += (
                    f'predictions_total{{sentiment="{sentiment}"}} {count}\n'
                )

            metrics_output += (
                "\n# HELP average_confidence Average prediction confidence\n"
            )
            metrics_output += "# TYPE average_confidence gauge\n"
            metrics_output += f"average_confidence {avg_conf}\n"

            # Add database pool status
            metrics_output += "\n# HELP db_pool_ready Database pool readiness\n"
            metrics_output += "# TYPE db_pool_ready gauge\n"
            metrics_output += f"db_pool_ready {1 if db_pool.is_ready() else 0}\n"

            return metrics_output
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        return "# Error generating metrics\n"


@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on application shutdown."""
    db_pool.close()
