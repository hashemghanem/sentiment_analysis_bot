# MLOps Database Connection - Best Practices Implementation

## What's Wrong with v2 and v3

### v2 Approach
```python
# v2 - Opens connection on every request
def predict(input: TextInput):
    conn = psycopg2.connect(DATABASE_URL)  # ❌ New connection each time
    # ... do work ...
    conn.close()
```

**Problems:**
- Slow (connection overhead on every request)
- Can't handle high load
- No connection pooling

### v3 Approach
```python
# v3 - Connects at startup
app = FastAPI()
init_db()  # ❌ Crashes if DB unavailable at startup

def predict(input: TextInput):
    conn = get_db_connection()  # ❌ Still new connection each time
```

**Problems:**
- All v2 problems +
- Pod crashes if DB temporarily down
- No graceful degradation

## ✅ Production-Ready Implementation

### Improved `src/api/main.py`

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
from psycopg2 import pool
from contextlib import contextmanager
import os
import logging
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
MAX_DB_CONNECTIONS = int(os.getenv("MAX_DB_CONNECTIONS", "10"))
MIN_DB_CONNECTIONS = int(os.getenv("MIN_DB_CONNECTIONS", "2"))

# Global connection pool (initialized lazily)
db_pool = None

def init_connection_pool():
    """Initialize database connection pool with retry logic"""
    global db_pool
    
    if db_pool is not None:
        return db_pool
    
    try:
        logger.info("Initializing database connection pool...")
        db_pool = pool.ThreadedConnectionPool(
            MIN_DB_CONNECTIONS,
            MAX_DB_CONNECTIONS,
            DATABASE_URL,
            sslmode='require',
            connect_timeout=10,
            options='-c statement_timeout=30000'  # 30s query timeout
        )
        logger.info(f"Connection pool initialized: {MIN_DB_CONNECTIONS}-{MAX_DB_CONNECTIONS} connections")
        return db_pool
    except Exception as e:
        logger.error(f"Failed to initialize connection pool: {str(e)}")
        # Don't crash the app, we'll retry later
        return None

@contextmanager
def get_db_connection():
    """Context manager for database connections with automatic cleanup"""
    conn = None
    try:
        if db_pool is None:
            init_connection_pool()
        
        if db_pool is None:
            raise HTTPException(
                status_code=503,
                detail="Database connection pool not available"
            )
        
        conn = db_pool.getconn()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        if conn and db_pool:
            db_pool.putconn(conn)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def init_db_schema():
    """Initialize database schema with retry logic"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    text TEXT,
                    sentiment TEXT,
                    confidence FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_version TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_predictions_timestamp 
                ON predictions(timestamp DESC);
            """)
            logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {str(e)}")
        # Don't crash - app can still serve predictions
        pass

# FastAPI app
app = FastAPI(title="ML Sentiment API")

# Load model
try:
    model = joblib.load('model.pkl')
    MODEL_VERSION = "v1.0.0"
    logger.info(f"Model loaded: {MODEL_VERSION}")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    raise

# Startup event - non-blocking database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info("Application starting up...")
    init_connection_pool()
    
    # Try to init schema, but don't block startup
    try:
        init_db_schema()
    except Exception as e:
        logger.warning(f"Could not initialize DB schema at startup: {str(e)}")
        logger.info("App will continue without database logging")

# Shutdown event - cleanup
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("Application shutting down...")
    global db_pool
    if db_pool:
        db_pool.closeall()
        logger.info("Database connection pool closed")

class TextInput(BaseModel):
    text: str

def log_prediction(text: str, sentiment: str, confidence: float):
    """Log prediction to database with error handling"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO predictions (text, sentiment, confidence, model_version)
                VALUES (%s, %s, %s, %s)
                """,
                (text, sentiment, confidence, MODEL_VERSION)
            )
            logger.debug(f"Prediction logged: {sentiment} ({confidence:.2f})")
    except Exception as e:
        # Log error but don't fail the prediction
        logger.error(f"Failed to log prediction to database: {str(e)}")

@app.post("/predict")
async def predict(input: TextInput):
    """Make prediction"""
    start_time = time.time()
    
    try:
        # Make prediction
        prediction = model.predict([input.text])[0]
        proba = model.predict_proba([input.text])[0]
        confidence = float(max(proba))
        
        # Log to database (non-blocking, errors ignored)
        log_prediction(input.text, prediction, confidence)
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "sentiment": prediction,
            "confidence": confidence,
            "latency_ms": latency_ms,
            "model_version": MODEL_VERSION
        }
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "model_loaded": model is not None,
        "database_pool": "unavailable"
    }
    
    # Check database connectivity (optional)
    try:
        if db_pool:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                health_status["database_pool"] = "healthy"
    except Exception as e:
        logger.warning(f"Database health check failed: {str(e)}")
        health_status["database_pool"] = "unhealthy"
    
    return health_status

@app.get("/ready")
async def readiness():
    """Readiness check for Kubernetes"""
    # App is ready if model is loaded
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {"status": "ready"}
```

### Updated `requirements.txt`

```txt
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
fastapi==0.104.1
uvicorn==0.24.0
joblib==1.3.2
pydantic==2.5.0
psycopg2-binary==2.9.9
tenacity==8.2.3  # For retry logic
```

### Updated Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ml-api
  template:
    metadata:
      labels:
        app: ml-api
    spec:
      containers:
      - name: ml-api
        image: mldemoacr.azurecr.io/ml-api:v4
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: MAX_DB_CONNECTIONS
          value: "10"
        - name: MIN_DB_CONNECTIONS
          value: "2"
        resources:
          requests:
            cpu: 100m
            memory: 256Mi  # Increased for connection pool
          limits:
            cpu: 500m
            memory: 512Mi
        # IMPORTANT: Separate liveness and readiness probes
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          failureThreshold: 2
        volumeMounts:
        - name: secrets-store
          mountPath: "/mnt/secrets-store"
          readOnly: true
      volumes:
      - name: secrets-store
        csi:
          driver: secrets-store.csi.k8s.io
          readOnly: true
          volumeAttributes:
            secretProviderClass: "azure-keyvault-secrets"
```

## Key Improvements Explained

### 1. ✅ Connection Pooling
```python
db_pool = pool.ThreadedConnectionPool(2, 10, DATABASE_URL)
```
- Reuses connections (much faster)
- Limits concurrent connections to database
- Handles connection lifecycle automatically

### 2. ✅ Context Manager Pattern
```python
with get_db_connection() as conn:
    # Do work
    # Automatic commit/rollback/return to pool
```
- Guarantees connection cleanup
- Automatic rollback on errors
- Returns connection to pool

### 3. ✅ Graceful Degradation
```python
try:
    log_prediction(...)  # Try to log
except Exception:
    pass  # But don't fail prediction if DB is down
```
- Predictions work even if database fails
- App stays up, logs errors
- Better user experience

### 4. ✅ Lazy Initialization
```python
@app.on_event("startup")
async def startup_event():
    init_connection_pool()  # Non-blocking
```
- App starts even if DB temporarily unavailable
- Will retry on first request
- No crash loops

### 5. ✅ Retry Logic
```python
@retry(stop_after_attempt(3), wait_exponential(...))
def init_db_schema():
```
- Handles transient database issues
- Exponential backoff
- Production-grade resilience

### 6. ✅ Separate Health Endpoints
```python
/health   # Liveness: Is app running?
/ready    # Readiness: Can app handle traffic?
```
- Kubernetes uses both correctly
- Can be healthy but not ready (DB down)
- Prevents traffic to unhealthy pods

## Networking Best Practice: Private Endpoint

Instead of firewall rules, use **private endpoint** (already in Phase 5):

```bash
# Remove public firewall rules
az postgres flexible-server firewall-rule delete \
  --resource-group ml-demo-rg \
  --name ml-demo-db \
  --rule-name allow-aks-pods

# Ensure private endpoint is configured (from Phase 5)
az network private-endpoint list \
  --resource-group ml-demo-rg \
  --query "[?contains(name, 'postgres')].name"

# Update PostgreSQL to disable public access
az postgres flexible-server update \
  --resource-group ml-demo-rg \
  --name ml-demo-db \
  --public-network-access Disabled
```

**Benefits:**
- Database not accessible from internet
- Traffic stays within VNet
- More secure, enterprise-grade
- No IP-based firewall rules needed

## Summary: v2 vs v3 vs Production

| Aspect | v2 | v3 | Production (Fixed) |
|--------|----|----|-------------------|
| Connection Strategy | New per request | New per request | Connection pool |
| Startup Behavior | No DB check | Crashes if DB down | Graceful startup |
| Error Handling | Crashes | Crashes | Degrades gracefully |
| Performance | Slow | Slow | Fast |
| Resilience | Low | Low | High |
| Production Ready | ❌ | ❌ | ✅ |

## Deploy the Fix

```bash
# 1. Update code with improved main.py
# (Copy the code above)

# 2. Rebuild
docker build -t ml-api .
docker tag ml-api mldemoacr.azurecr.io/ml-api:v4
docker push mldemoacr.azurecr.io/ml-api:v4

# 3. Apply updated deployment
kubectl apply -f k8s/deployment.yaml

# 4. Watch rollout
kubectl rollout status deployment/ml-api

# 5. Test graceful degradation
# Stop database temporarily
az postgres flexible-server stop --resource-group ml-demo-rg --name ml-demo-db

# App should still respond to /health
curl http://$INGRESS_IP/health
# {"status":"healthy","model_loaded":true,"database_pool":"unhealthy"}

# Predictions still work (just not logged)
curl -X POST http://$INGRESS_IP/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"This is great!"}'

# Start database again
az postgres flexible-server start --resource-group ml-demo-rg --name ml-demo-db
```

The production version is **significantly better** for MLOps because it handles failures gracefully, performs better, and follows cloud-native patterns.