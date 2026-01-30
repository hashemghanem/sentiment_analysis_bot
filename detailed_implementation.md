
# Azure ML Project - Incremental Implementation Guide

## MLOps Philosophy: Start Simple, Iterate Fast

Each phase delivers a **working system** that you can demonstrate and use. No phase depends on future work being complete.

---

## 🎯 MLOps Engineer's Deployment Choice

**If I were an MLOps engineer, I would deploy on: Azure Container Apps**

**Why?**

"It gives you containers and auto-scaling without managing Kubernetes infrastructure."

### Detailed Reasoning:

**For this specific project:**
- **Simplicity**: No node pool management, no ingress configuration
- **Cost**: Pay-per-request pricing (~$30-50/month vs $100+ for AKS)
- **Auto-scaling**: Built-in, no HPA configuration needed
- **Managed**: Azure handles updates, security patches, certificates
- **Fast deployment**: `az containerapp up` and you're done

**However, AKS is better when:**
- You need complex networking (service mesh, multiple namespaces)
- Running 10+ microservices
- Need full Kubernetes control (CRDs, operators)
- Team already knows Kubernetes
- Multi-cloud strategy (Kubernetes is portable)

**For learning purposes:**
- **Choose AKS** - you want to practice Kubernetes ✅
- **Choose Container Apps** - you want to ship fast in production

**The Reality Check:**
- **For a startup/small team**: Container Apps or Azure Functions (serverless)
- **For an enterprise with K8s expertise**: AKS
- **For a solo developer learning**: Start with Container Apps, then learn AKS
- **For maximum portability**: AKS (Kubernetes runs anywhere)

**Bottom line**: AKS is a great learning investment and essential for your resume, but for a simple ML API in production, Container Apps would be more cost-effective and easier to maintain. However, once you learn AKS, you can apply that knowledge to any cloud provider (EKS, GKE) or on-premises.

---

## 🚀 Quick Start Guide

### Ready to Begin? Start Here:

#### Option A: Full Learning Path (Recommended for You)
Follow Phase 0 → Phase 7 to learn everything

**Week 1**: Local dev + AKS deployment + Database
**Week 2**: Terraform automation
**Week 3**: Advanced Kubernetes + Monitoring  
**Week 4**: Security + Automation

#### Option B: Fast Track to Production
Skip to Container Apps alternative:

```bash
# 1. Build locally
docker build -t ml-api .

# 2. Create Container App environment
az containerapp env create \
  --name ml-env \
  --resource-group ml-demo-rg \
  --location eastus

# 3. Deploy
az containerapp create \
  --name ml-api \
  --resource-group ml-demo-rg \
  --environment ml-env \
  --image mldemoacr.azurecr.io/ml-api:v1 \
  --target-port 8000 \
  --ingress external \
  --registry-server mldemoacr.azurecr.io \
  --min-replicas 0 \
  --max-replicas 3

# Done! Get URL:
az containerapp show \
  --name ml-api \
  --resource-group ml-demo-rg \
  --query properties.configuration.ingress.fqdn
```

**Cost comparison:**
- Container Apps: $0 when idle, ~$30-50/month under load
- AKS: ~$100-165/month (always running)

---

## 📚 Learning Resources by Phase

### Phase 0 - ML Basics
- scikit-learn documentation
- FastAPI tutorial
- Python type hints

### Phase 1 - AKS Fundamentals
- [AKS Workshop](https://docs.microsoft.com/azure/aks/tutorial-kubernetes-prepare-app)
- [Kubernetes basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- Docker documentation

### Phase 2 - Databases
- PostgreSQL on Azure docs
- Connection pooling best practices
- SQL injection prevention

### Phase 3 - Terraform
- [Terraform AKS tutorial](https://learn.hashicorp.com/tutorials/terraform/aks)
- HashiCorp best practices
- Remote state management

### Phase 4 - Advanced Kubernetes
- Ingress controllers comparison
- HPA tuning guide
- Resource management

### Phase 5 - Security
- Azure Key Vault integration
- RBAC concepts
- Network security groups

### Phase 6 - Monitoring
- Application Insights setup
- Grafana dashboards
- Prometheus metrics

### Phase 7 - MLOps
- Model versioning strategies
- A/B testing patterns
- Continuous training pipelines

---

## 🎓 Skills You'll Master

### Infrastructure Skills
✅ Azure cloud services (AKS, ACR, PostgreSQL, Key Vault)
✅ Kubernetes orchestration (pods, services, ingress, HPA)
✅ Terraform infrastructure as code
✅ Networking (VNets, subnets, private endpoints)
✅ Security (RBAC, secrets management, network policies)

### ML/DevOps Skills
✅ Containerization with Docker
✅ ML model serving with FastAPI
✅ Automated retraining pipelines
✅ Model versioning and deployment
✅ Monitoring and observability

### Best Practices
✅ GitOps workflows
✅ Infrastructure as Code
✅ Secrets management
✅ Resource optimization
✅ Cost management

---

## 💰 Cost Management Tips

### Development Phase
1. **Use dev/test pricing** for VMs when available
2. **Stop AKS at night**: Scale node pool to 0
3. **Use Azure DevTest subscription** if available
4. **Set budget alerts** in Azure Cost Management
5. **Delete resources** when not actively working

### Cost Optimization Commands
```bash
# Scale down AKS nodes (nights/weekends)
az aks scale \
  --resource-group ml-demo-rg \
  --name ml-demo-aks \
  --node-count 0

# Scale back up
az aks scale \
  --resource-group ml-demo-rg \
  --name ml-demo-aks \
  --node-count 1

# Stop PostgreSQL (if supported in your tier)
az postgres flexible-server stop \
  --resource-group ml-demo-rg \
  --name ml-demo-db

# View costs
az consumption usage list \
  --start-date 2025-10-01 \
  --end-date 2025-10-27
```

### Estimated Daily Costs
- **Active development**: ~$5-7/day
- **Idle (scaled down)**: ~$1-2/day
- **Fully deleted**: $0

**Pro tip**: Use Terraform to destroy everything on Friday evening and recreate on Monday morning. Total cost for a month of weekend learning: ~$100-150.

---

## 🐛 Common Issues & Solutions

### Issue 1: AKS Node Not Ready
```bash
# Check node status
kubectl get nodes
kubectl describe node <node-name>

# Common fix: Wait 5-10 minutes for provisioning
# Or restart the node pool
az aks nodepool stop --cluster-name ml-demo-aks ...
az aks nodepool start --cluster-name ml-demo-aks ...
```

### Issue 2: Image Pull Errors
```bash
# Verify ACR attachment
az aks check-acr \
  --resource-group ml-demo-rg \
  --name ml-demo-aks \
  --acr mldemoacr.azurecr.io

# Reattach if needed
az aks update \
  --resource-group ml-demo-rg \
  --name ml-demo-aks \
  --attach-acr mldemoacr
```

### Issue 3: Database Connection Fails
```bash
# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group ml-demo-rg \
  --name ml-demo-db

# Add AKS outbound IP
kubectl get service -n ingress-nginx
# Use that IP in firewall rule
```

### Issue 4: Ingress Not Getting IP
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx <controller-pod>

# Reinstall if needed
helm uninstall ingress-nginx -n ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx ...
```

### Issue 5: Terraform State Locked
```bash
# Break lease (use carefully!)
az storage blob lease break \
  --container-name tfstate \
  --blob-name terraform.tfstate \
  --account-name mldemotfstate
```

---

## 🎯 Next Steps After Completion

### Level Up Your Project
1. **Add CI/CD pipeline** (GitHub Actions or Azure DevOps)
2. **Implement A/B testing** for model versions
3. **Add model explainability** (SHAP, LIME)
4. **Create data drift detection**
5. **Add more sophisticated ML models** (transformers, ensemble methods)

### Expand to More Services
1. **Azure Service Bus** for async processing
2. **Azure Blob Storage** for large file uploads
3. **Azure Cognitive Services** integration
4. **Azure ML workspace** for experiment tracking

### Career Development
1. **Write blog posts** about what you learned
2. **Create GitHub repo** with documentation
3. **Get Azure certifications** (AZ-104, AZ-305, AI-102)
4. **Present at meetups** about your project
5. **Add to resume/LinkedIn** with specific metrics

---

## 📞 Getting Help

### When You're Stuck
1. **Azure documentation**: docs.microsoft.com/azure
2. **Kubernetes docs**: kubernetes.io/docs
3. **Stack Overflow**: Tag questions appropriately
4. **Azure Discord/Slack**: Active communities
5. **GitHub Issues**: Check official repos

### Debugging Checklist
- [ ] Check pod logs: `kubectl logs <pod-name>`
- [ ] Describe resources: `kubectl describe <resource>`
- [ ] Check events: `kubectl get events --sort-by='.lastTimestamp'`
- [ ] Verify networking: `kubectl exec -it <pod> -- curl <service>`
- [ ] Check Azure portal for resource status
- [ ] Review Terraform plan before apply
- [ ] Test locally before deploying to cloud

---

## ✨ Final Encouragement

This project covers **a lot** of ground. Don't expect to master everything in one pass. The key is to:

1. **Get something working** at each phase
2. **Understand why it works** (not just copy-paste)
3. **Break things and fix them** (best way to learn)
4. **Document your learnings** (for future you)
5. **Iterate and improve** over time

Remember: Even experienced engineers Google basic Kubernetes commands. The goal isn't to memorize everything—it's to understand the concepts and know where to find answers.

**You've got this! Start with Phase 0 and build from there.** 🚀

---

Ready to start? Let me know which phase you want to dive into first, and I can provide more detailed step-by-step instructions!

## 🎯 Phase 0: Local Development (Week 1, Days 1-2)
**Goal**: Working ML model on your laptop

### What You'll Build
- Simple sentiment analysis model
- Basic FastAPI application
- Local testing with sample data

### Why Start Here?
- Validate the ML approach works
- Debug quickly without cloud costs
- Understand the core functionality

### Implementation Steps

#### 1. Create Project Structure
```bash
mkdir azure-ml-project && cd azure-ml-project
mkdir -p src/model src/api tests data

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
# requirements.txt
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
fastapi==0.104.1
uvicorn==0.24.0
joblib==1.3.2
pydantic==2.5.0
```

#### 3. Build Simple Model (`src/model/train.py`)
```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# Simple training data
data = [
    ("I love this product", "positive"),
    ("This is amazing", "positive"),
    ("Terrible experience", "negative"),
    ("Waste of money", "negative"),
    # Add 20-30 more examples
]

df = pd.DataFrame(data, columns=['text', 'sentiment'])

# Create simple pipeline
model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=1000)),
    ('classifier', LogisticRegression())
])

model.fit(df['text'], df['sentiment'])
joblib.dump(model, 'model.pkl')
print("✅ Model trained and saved!")
```

#### 4. Create API (`src/api/main.py`)
```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()
model = joblib.load('model.pkl')

class TextInput(BaseModel):
    text: str

@app.post("/predict")
def predict(input: TextInput):
    prediction = model.predict([input.text])[0]
    return {"sentiment": prediction}

@app.get("/health")
def health():
    return {"status": "healthy"}
```

#### 5. Test Locally
```bash
# Run API
uvicorn src.api.main:app --reload

# Test in another terminal
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text":"This is great!"}'
```

### ✅ Phase 0 Complete When:
- Model trains successfully
- API returns predictions
- You understand the core logic

**Time Investment**: 4-6 hours

---

## 🚀 Phase 1: Minimal Azure Deployment (Week 1, Days 3-5)
**Goal**: API running in AKS (simplest Kubernetes setup)

### What You'll Build
- Azure Kubernetes Service (single node)
- Azure Container Registry
- Dockerized API
- Basic Kubernetes deployment
- **NO** Terraform, VNet, databases yet

### Why Start with AKS Instead of VM?
- **You want to learn AKS** - this is your goal!
- Still simple - just 1 node to start
- Same cost as VM (~$25/month for Standard_B2s)
- Learn Kubernetes concepts early
- Easier to scale later

### Why This Approach Works
- AKS basics without complexity
- Manual setup teaches fundamentals
- See pods, services, deployments in action

### Implementation Steps

#### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY model.pkl .

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Test Docker Locally
```bash
docker build -t ml-api .
docker run -p 8000:8000 ml-api

# Test it works
curl http://localhost:8000/health
```

#### 3. Deploy to Azure AKS (Manual - CLI)
```bash
# 1. Create resource group
az group create --name ml-demo-rg --location eastus

# 2. Create Azure Container Registry
az acr create \
  --resource-group ml-demo-rg \
  --name mldemoacr \
  --sku Basic

# 3. Create AKS cluster (single node, simple)
az aks create \
  --resource-group ml-demo-rg \
  --name ml-demo-aks \
  --node-count 1 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys \
  --attach-acr mldemoacr

# 4. Get AKS credentials
az aks get-credentials --resource-group ml-demo-rg --name ml-demo-aks

# 5. Verify connection
kubectl get nodes
# You should see 1 node in Ready state
```

#### 4. Push Docker Image to ACR
```bash
# Login to ACR
az acr login --name mldemoacr

# Tag your image
docker tag ml-api mldemoacr.azurecr.io/ml-api:v1

# Push to ACR
docker push mldemoacr.azurecr.io/ml-api:v1

# Verify
az acr repository list --name mldemoacr --output table
```

#### 5. Create Kubernetes Manifests

Create `k8s/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-api
  labels:
    app: ml-api
spec:
  replicas: 1  # Start with 1 pod
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
        image: mldemoacr.azurecr.io/ml-api:v1
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ml-api-service
spec:
  type: LoadBalancer  # This creates a public IP
  selector:
    app: ml-api
  ports:
  - protocol: TCP
    port: 80        # External port
    targetPort: 8000  # Container port
```

#### 6. Deploy to Kubernetes
```bash
# Apply the manifests
kubectl apply -f k8s/deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get pods

# Wait for pod to be Running
kubectl get pods -w

# Check service and get external IP
kubectl get services
# Wait for EXTERNAL-IP (takes 2-3 minutes)

# Test your API
EXTERNAL_IP=$(kubectl get service ml-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$EXTERNAL_IP/health
curl -X POST http://$EXTERNAL_IP/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"This is amazing!"}'
```

#### 7. Useful Kubernetes Commands
```bash
# View pod logs
kubectl logs -l app=ml-api

# Follow logs in real-time
kubectl logs -l app=ml-api -f

# Describe pod (troubleshooting)
kubectl describe pod <pod-name>

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/bash

# View all resources
kubectl get all

# Delete everything (cleanup)
kubectl delete -f k8s/deployment.yaml
```

### ✅ Phase 1 Complete When:
- AKS cluster is running
- Pod is in "Running" state
- Service has external IP assigned
- You can make predictions via LoadBalancer IP
- You understand: pods, deployments, services

**Kubernetes Concepts You've Learned:**
- **Deployment**: Manages pod replicas and rolling updates
- **Pod**: Container runtime (your API runs here)
- **Service**: Network abstraction and load balancing
- **LoadBalancer**: Azure-managed external IP

**Time Investment**: 6-8 hours

---

## 📊 Phase 2: Add Database (Week 1, Days 6-7)
**Goal**: Store prediction logs

### What You'll Add
- Azure Database for PostgreSQL (Basic tier)
- Logging predictions to database
- Simple query interface

### Why This Phase?
- Learn Azure database provisioning
- Practice connection strings and secrets
- Collect data for future retraining

### Implementation Steps

#### 1. Create PostgreSQL Database
```bash
az postgres flexible-server create \
  --resource-group ml-demo-rg \
  --name ml-demo-db \
  --location eastus \
  --admin-user myadmin \
  --admin-password <SecurePassword123!> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14 \
  --storage-size 32 \
  --public-access 0.0.0.0

# Create database
az postgres flexible-server db create \
  --resource-group ml-demo-rg \
  --server-name ml-demo-db \
  --database-name predictions
```

#### 2. Update API to Log Predictions
```python
# Add to requirements.txt
psycopg2-binary==2.9.9

# Update src/api/main.py
import psycopg2
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def log_prediction(text, sentiment):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            text TEXT,
            sentiment TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute(
        "INSERT INTO predictions (text, sentiment) VALUES (%s, %s)",
        (text, sentiment)
    )
    conn.commit()
    conn.close()

@app.post("/predict")
def predict(input: TextInput):
    prediction = model.predict([input.text])[0]
    log_prediction(input.text, prediction)
    return {"sentiment": prediction}
```

#### 3. Redeploy with Database Connection
```bash
# Create Kubernetes secret for database
kubectl create secret generic db-secret \
  --from-literal=database-url="postgresql://myadmin:<password>@ml-demo-db.postgres.database.azure.com/predictions"

# Update deployment to use secret
# Edit k8s/deployment.yaml and add:
#   env:
#   - name: DATABASE_URL
#     valueFrom:
#       secretKeyRef:
#         name: db-secret
#         key: database-url

# Rebuild and push new image
docker build -t ml-api .
docker tag ml-api mldemoacr.azurecr.io/ml-api:v2
docker push mldemoacr.azurecr.io/ml-api:v2

# Update deployment
kubectl set image deployment/ml-api ml-api=mldemoacr.azurecr.io/ml-api:v2

# Watch rollout
kubectl rollout status deployment/ml-api

# Test predictions are logged
kubectl logs -l app=ml-api
```

### ✅ Phase 2 Complete When:
- Predictions are logged to database
- You can query prediction history
- Connection is secure

**Time Investment**: 4-6 hours

---

## 🏗️ Phase 3: Infrastructure as Code (Week 2)
**Goal**: Automate everything with Terraform

### What You'll Add
- Terraform configuration for AKS + ACR + PostgreSQL
- Remote state storage
- Reproducible infrastructure
- VNet integration

### Why This Phase?
- Destroy and recreate easily
- Version control infrastructure
- Learn Terraform properly
- Add networking layer

### Implementation Steps

#### 1. Setup Terraform Structure
```bash
mkdir terraform && cd terraform

# Create backend storage first (manual, one-time)
az storage account create \
  --name mldemotfstate \
  --resource-group ml-demo-rg \
  --location eastus \
  --sku Standard_LRS

az storage container create \
  --name tfstate \
  --account-name mldemotfstate
```

#### 2. Create `terraform/main.tf`
```hcl
terraform {
  required_version = ">= 1.0"
  
  backend "azurerm" {
    resource_group_name  = "ml-demo-rg"
    storage_account_name = "mldemotfstate"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "ml-demo-rg"
  location = "eastus"
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "ml-demo-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "aks" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Azure Container Registry
resource "azurerm_container_registry" "main" {
  name                = "mldemoacr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = false
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "ml-demo-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "ml-demo"
  
  default_node_pool {
    name           = "default"
    node_count     = 1
    vm_size        = "Standard_B2s"
    vnet_subnet_id = azurerm_subnet.aks.id
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  linux_profile {
    admin_username = "azureuser"
    ssh_key {
      key_data = file("~/.ssh/id_rsa.pub")
    }
  }
  
  network_profile {
    network_plugin = "azure"
    network_policy = "azure"
  }
}

# Grant AKS access to ACR
resource "azurerm_role_assignment" "aks_acr" {
  principal_id                     = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.main.id
  skip_service_principal_aad_check = true
}

# PostgreSQL
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "ml-demo-db"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "14"
  administrator_login    = "myadmin"
  administrator_password = var.db_password
  
  storage_mb = 32768
  sku_name   = "B_Standard_B1ms"
  
  backup_retention_days = 7
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "predictions"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Outputs
output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "acr_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "postgresql_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}
```

Create `terraform/variables.tf`:
```hcl
variable "db_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}
```

#### 3. Apply Terraform
```bash
# Set password
export TF_VAR_db_password="YourSecurePassword123!"

terraform init
terraform plan
terraform apply

# Get AKS credentials
az aks get-credentials \
  --resource-group ml-demo-rg \
  --name ml-demo-aks \
  --overwrite-existing

# Now you can destroy and recreate anytime!
terraform destroy  # When needed
```

### ✅ Phase 3 Complete When:
- All infrastructure is in Terraform (AKS, ACR, VNet, PostgreSQL)
- State is stored remotely
- VNet integration is working
- You can destroy/recreate in minutes

**Time Investment**: 8-10 hours

---

## 🎭 Phase 4: Advanced Kubernetes Features (Week 3)
**Goal**: Production-ready Kubernetes setup

### What You'll Add
- Multiple replicas with auto-scaling
- Ingress controller (instead of LoadBalancer)
- ConfigMaps and proper secret management
- Resource quotas and limits
- Liveness and readiness probes refined

### Implementation Steps

#### 1. Install NGINX Ingress Controller
```bash
# Add Helm repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install ingress controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --create-namespace \
  --namespace ingress-nginx \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz

# Wait for external IP
kubectl get services -n ingress-nginx -w
```

#### 2. Update Deployment with Auto-scaling
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-api
spec:
  replicas: 2  # Increase to 2
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
        image: mldemoacr.azurecr.io/ml-api:v2
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: database-url
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: ml-api-service
spec:
  type: ClusterIP  # Changed from LoadBalancer
  selector:
    app: ml-api
  ports:
  - port: 80
    targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ml-api-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ml-api-service
            port:
              number: 80
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-api
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

#### 3. Apply Updates
```bash
kubectl apply -f k8s/deployment.yaml

# Check HPA status
kubectl get hpa

# Get ingress IP
kubectl get ingress
INGRESS_IP=$(kubectl get ingress ml-api-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test
curl http://$INGRESS_IP/health
```

### ✅ Phase 4 Complete When:
- Ingress controller is working
- Multiple replicas running
- HPA scales pods based on CPU
- Service accessible via Ingress IP

**Kubernetes Concepts Added:**
- **Ingress**: HTTP routing and load balancing
- **HPA**: Automatic horizontal scaling
- **ClusterIP**: Internal service networking

**Time Investment**: 6-8 hours

---




# Detailed Implementation Guide - Phases 5, 6, 7

You've completed Phase 4! Now let's implement the remaining phases with exact, copy-paste commands.

---

## 🔒 PHASE 5: Security & Networking (Detailed Steps)

**Current State:** AKS with Ingress, HPA, multiple replicas
**Goal:** Add Key Vault, private endpoints, RBAC, network policies

### Step 5.1: Create Azure Key Vault

```bash
# 1. Create Key Vault
az keyvault create \
  --name ml-demo-kv-$(date +%s) \
  --resource-group ml-demo-rg \
  --location eastus \
  --enable-rbac-authorization true

# Note the Key Vault name (it must be globally unique)
KV_NAME="ml-demo-kv-1234567890"  # Replace with your actual name

# 2. Get your user's Object ID
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

# 3. Grant yourself Key Vault Administrator role
az role assignment create \
  --role "Key Vault Administrator" \
  --assignee $USER_OBJECT_ID \
  --scope $(az keyvault show --name $KV_NAME --resource-group ml-demo-rg --query id -o tsv)

# 4. Wait 60 seconds for RBAC to propagate
sleep 60

# 5. Store database connection string as secret
az keyvault secret set \
  --vault-name $KV_NAME \
  --name "database-url" \
  --value "postgresql://myadmin:YourPassword123!@ml-demo-db.postgres.database.azure.com/predictions"
```

### Step 5.2: Install CSI Secret Store Driver

```bash
# 1. Enable the Azure Key Vault Provider for Secrets Store CSI Driver
az aks enable-addons \
  --resource-group ml-demo-rg \
  --name ml-demo-aks \
  --addons azure-keyvault-secrets-provider

# 2. Verify installation
kubectl get pods -n kube-system -l app=secrets-store-csi-driver
kubectl get pods -n kube-system -l app=secrets-store-provider-azure

# Should see pods in Running state
```

### Step 5.3: Configure AKS to Access Key Vault

```bash
# 1. Get AKS cluster identity
AKS_IDENTITY=$(az aks show \
  --resource-group ml-demo-rg \
  --name ml-demo-aks \
  --query addonProfiles.azureKeyvaultSecretsProvider.identity.clientId -o tsv)

echo "AKS Identity Client ID: $AKS_IDENTITY"

# 2. Grant AKS identity access to Key Vault
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $AKS_IDENTITY \
  --scope $(az keyvault show --name $KV_NAME --resource-group ml-demo-rg --query id -o tsv)

# 3. Get Key Vault tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)

echo "Tenant ID: $TENANT_ID"
```

### Step 5.4: Create SecretProviderClass

Create file `k8s/secret-provider.yaml`:

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: azure-keyvault-secrets
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "true"
    userAssignedIdentityID: "<AKS_IDENTITY>"  # Replace with actual value
    keyvaultName: "<KV_NAME>"                  # Replace with actual value
    cloudName: ""
    objects: |
      array:
        - |
          objectName: database-url
          objectType: secret
          objectVersion: ""
    tenantId: "<TENANT_ID>"                    # Replace with actual value
  secretObjects:
  - secretName: db-secret-from-kv
    type: Opaque
    data:
    - objectName: database-url
      key: database-url
```

**Replace placeholders:**
```bash
# Get the values
echo "AKS_IDENTITY: $AKS_IDENTITY"
echo "KV_NAME: $KV_NAME"
echo "TENANT_ID: $TENANT_ID"

# Edit the file and replace <AKS_IDENTITY>, <KV_NAME>, <TENANT_ID>
# Or use sed (on Linux/Mac):
sed -i "s/<AKS_IDENTITY>/$AKS_IDENTITY/g" k8s/secret-provider.yaml
sed -i "s/<KV_NAME>/$KV_NAME/g" k8s/secret-provider.yaml
sed -i "s/<TENANT_ID>/$TENANT_ID/g" k8s/secret-provider.yaml
```

Apply it:
```bash
kubectl apply -f k8s/secret-provider.yaml

# Verify
kubectl get secretproviderclass
```

### Step 5.5: Update Deployment to Use Key Vault

Create file `k8s/deployment-with-keyvault.yaml`:

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
        image: mldemoacr.azurecr.io/ml-api:v2
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret-from-kv
              key: database-url
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
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

Apply the update:
```bash
# Delete old secret (we're using Key Vault now)
kubectl delete secret db-secret --ignore-not-found

# Apply new deployment
kubectl apply -f k8s/deployment-with-keyvault.yaml

# Watch rollout
kubectl rollout status deployment/ml-api

# Verify pods are running
kubectl get pods

# Check if secret was created
kubectl get secret db-secret-from-kv

# Test the API still works
INGRESS_IP=$(kubectl get ingress ml-api-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$INGRESS_IP/health
```

### Step 5.6: Add Network Policies

Create file `k8s/network-policy.yaml`:

```yaml
# Default deny all ingress traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
---
# Allow traffic to ml-api from ingress controller
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-to-api
spec:
  podSelector:
    matchLabels:
      app: ml-api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  - from:
    - podSelector:
        matchLabels:
          app: ml-api
    ports:
    - protocol: TCP
      port: 8000
---
# Allow egress to internet (for database connections)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-egress
spec:
  podSelector:
    matchLabels:
      app: ml-api
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector: {}
  - to:
    - podSelector: {}
  - ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 443   # HTTPS
    - protocol: TCP
      port: 53    # DNS
    - protocol: UDP
      port: 53    # DNS
```

Apply network policies:
```bash
# Label the ingress-nginx namespace
kubectl label namespace ingress-nginx name=ingress-nginx

# Apply policies
kubectl apply -f k8s/network-policy.yaml

# Verify
kubectl get networkpolicies

# Test API still works (it should)
curl http://$INGRESS_IP/health
```

### Step 5.7: Configure RBAC for AKS

Create roles for different team members with appropriate permissions:

```bash
# 1. Create ClusterRole for read-only access (for developers/viewers)
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ml-api-reader
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get", "list"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch"]
EOF

# 2. Bind the reader role to an Azure AD group (for your team)
# First, get your Azure AD group Object ID
AD_GROUP_ID=$(az ad group show \
  --group "ML-Team-Readers" \
  --query id -o tsv 2>/dev/null || echo "")

if [ -z "$AD_GROUP_ID" ]; then
  echo "Azure AD group 'ML-Team-Readers' doesn't exist. Creating it..."
  az ad group create \
    --display-name "ML-Team-Readers" \
    --mail-nickname "ml-team-readers"
  
  AD_GROUP_ID=$(az ad group show \
    --group "ML-Team-Readers" \
    --query id -o tsv)
fi

echo "AD Group Object ID: $AD_GROUP_ID"

# 3. Create ClusterRoleBinding to assign reader role to AD group
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ml-api-reader-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: ml-api-reader
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: "$AD_GROUP_ID"  # Azure AD Group Object ID
EOF

# 4. Create a service account for deployment automation (CI/CD pipelines)
kubectl create serviceaccount ml-api-deployer

# 5. Create ClusterRoleBinding for deployer (needs edit permissions)
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ml-api-deployer-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: edit
subjects:
- kind: ServiceAccount
  name: ml-api-deployer
  namespace: default
EOF

# 6. Create token for deployer service account (for CI/CD)
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: ml-api-deployer-token
  annotations:
    kubernetes.io/service-account.name: ml-api-deployer
type: kubernetes.io/service-account-token
EOF

# 7. Get the token (save this for CI/CD pipeline)
kubectl get secret ml-api-deployer-token -o jsonpath='{.data.token}' | base64 -d
echo ""
echo "Save this token for your CI/CD pipeline!"

# 8. Verify RBAC setup
echo ""
echo "=== RBAC Verification ==="
echo "ClusterRoles:"
kubectl get clusterroles | grep ml-api

echo ""
echo "ClusterRoleBindings:"
kubectl get clusterrolebindings | grep ml-api

echo ""
echo "Service Accounts:"
kubectl get serviceaccounts | grep ml-api
```

### Use Case Examples for RBAC Roles

**Example 1: Add a developer to the reader group**
```bash
# Add a user to Azure AD group
USER_EMAIL="developer@company.com"
USER_ID=$(az ad user show --id $USER_EMAIL --query id -o tsv)

az ad group member add \
  --group "ML-Team-Readers" \
  --member-id $USER_ID

# Now that developer can:
# - View pods: kubectl get pods
# - View logs: kubectl logs <pod-name>
# - View deployments: kubectl get deployments
# But CANNOT:
# - Delete pods: kubectl delete pod <pod-name> ❌ (Forbidden)
# - Edit deployments: kubectl edit deployment ml-api ❌ (Forbidden)
```

**Example 2: Test reader permissions**
```bash
# Simulate reader access (impersonate)
kubectl auth can-i get pods --as=ml-team-reader
# Output: yes

kubectl auth can-i delete pods --as=ml-team-reader
# Output: no

kubectl auth can-i get logs --as=ml-team-reader
# Output: yes

kubectl auth can-i edit deployments --as=ml-team-reader
# Output: no
```

**Example 3: Use deployer service account in CI/CD**
```bash
# In your GitHub Actions or Azure DevOps pipeline:

# Get cluster credentials
az aks get-credentials --resource-group ml-demo-rg --name ml-demo-aks

# Use service account token
DEPLOYER_TOKEN=$(kubectl get secret ml-api-deployer-token -o jsonpath='{.data.token}' | base64 -d)

# Configure kubectl to use this token
kubectl config set-credentials ml-api-deployer --token=$DEPLOYER_TOKEN

# Now your CI/CD can deploy
kubectl set image deployment/ml-api ml-api=mldemoacr.azurecr.io/ml-api:v6
```

### Step 5.8: Add Private Endpoint for PostgreSQL (Terraform)

Update your `terraform/main.tf` to add private endpoint:

```hcl
# Add after your existing PostgreSQL resource

# Create subnet for private endpoints
resource "azurerm_subnet" "private_endpoints" {
  name                 = "private-endpoints-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.5.0/24"]
}

# Create private DNS zone for PostgreSQL
resource "azurerm_private_dns_zone" "postgres" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
}

# Link DNS zone to VNet
resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                  = "postgres-dns-link"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.postgres.name
  virtual_network_id    = azurerm_virtual_network.main.id
}

# Create private endpoint
resource "azurerm_private_endpoint" "postgres" {
  name                = "ml-demo-db-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints.id

  private_service_connection {
    name                           = "postgres-pe-connection"
    private_connection_resource_id = azurerm_postgresql_flexible_server.main.id
    is_manual_connection           = false
    subresource_names              = ["postgresqlServer"]
  }

  private_dns_zone_group {
    name                 = "postgres-dns-zone-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.postgres.id]
  }
}

# Update PostgreSQL to disable public access
resource "azurerm_postgresql_flexible_server" "main" {
  # ... existing configuration ...
  
  # Add this:
  public_network_access_enabled = false
}
```

Apply Terraform changes:
```bash
cd terraform
terraform plan
terraform apply

# Wait for changes to complete (5-10 minutes)
```

### ✅ Phase 5 Complete Checklist

```bash
# Verify everything works
echo "=== Phase 5 Verification ==="

# 1. Key Vault secrets
echo "1. Key Vault secrets:"
az keyvault secret list --vault-name $KV_NAME --query "[].name"

# 2. Pods using secrets from Key Vault
echo "2. Pods with Key Vault secrets:"
kubectl get pods -l app=ml-api -o jsonpath='{.items[0].spec.volumes[?(@.csi)].csi.volumeAttributes.secretProviderClass}'

# 3. Network policies active
echo "3. Network policies:"
kubectl get networkpolicies

# 4. RBAC configured
echo "4. RBAC roles:"
kubectl get clusterroles | grep ml-api

# 5. API still works
echo "5. API health check:"
curl http://$INGRESS_IP/health

# 6. Private endpoint for database
echo "6. PostgreSQL private endpoint:"
az network private-endpoint list --resource-group ml-demo-rg --query "[?contains(name, 'postgres')].name"
```

**Time taken:** 2-3 hours

---

## 📈 PHASE 6: Monitoring (Detailed Steps)

**Goal:** Add Application Insights, Prometheus, and Grafana

### Step 6.1: Create Application Insights

```bash
# 1. Create Log Analytics Workspace
az monitor log-analytics workspace create \
  --resource-group ml-demo-rg \
  --workspace-name ml-demo-logs \
  --location eastus

# 2. Get workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group ml-demo-rg \
  --workspace-name ml-demo-logs \
  --query id -o tsv)

# 3. Create Application Insights
az monitor app-insights component create \
  --app ml-demo-insights \
  --location eastus \
  --resource-group ml-demo-rg \
  --workspace $WORKSPACE_ID

# 4. Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app ml-demo-insights \
  --resource-group ml-demo-rg \
  --query instrumentationKey -o tsv)

echo "Instrumentation Key: $INSTRUMENTATION_KEY"

# 5. Get connection string
CONNECTION_STRING=$(az monitor app-insights component show \
  --app ml-demo-insights \
  --resource-group ml-demo-rg \
  --query connectionString -o tsv)

echo "Connection String: $CONNECTION_STRING"
```

### Step 6.2: Enable Container Insights on AKS

```bash
# Enable monitoring addon
az aks enable-addons \
  --resource-group ml-demo-rg \
  --name ml-demo-aks \
  --addons monitoring \
  --workspace-resource-id $WORKSPACE_ID

# Verify
kubectl get pods -n kube-system | grep oms
```

### Step 6.3: Update Application to Use Application Insights

First, update the database schema to include the `confidence` column that the enhanced API will use:

```bash
# Get PostgreSQL server details
DB_SERVER="ml-demo-db"
DB_NAME="predictions"
DB_ADMIN="myadmin"

# Add the confidence column to the predictions table
az postgres flexible-server execute \
  --name $DB_SERVER \
  --resource-group ml-demo-rg \
  --admin-user $DB_ADMIN \
  --admin-password "<YourPassword>" \
  --database-name $DB_NAME \
  --querytext "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS confidence FLOAT;"

# Verify the updated schema
az postgres flexible-server execute \
  --name $DB_SERVER \
  --resource-group ml-demo-rg \
  --admin-user $DB_ADMIN \
  --admin-password "<YourPassword>" \
  --database-name $DB_NAME \
  --querytext "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'predictions' ORDER BY ordinal_position;"
```

Now update `src/api/main.py`:

```python
from fastapi import FastAPI, Response
from pydantic import BaseModel
import joblib
from psycopg2 import pool
import psycopg2
from datetime import datetime
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
import logging
import time
import threading
from contextlib import contextmanager

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
    "prediction_latency",
    "Latency of prediction requests",
    "ms"
)

# Create views
prediction_view = view_module.View(
    "prediction_latency_view",
    "Latency of predictions",
    [],
    prediction_measure,
    aggregation_module.LastValueAggregation()
)

view_manager.register_view(prediction_view)

# Create metrics exporter
if CONNECTION_STRING:
    exporter = metrics_exporter.new_metrics_exporter(
        connection_string=CONNECTION_STRING
    )
    view_manager.register_exporter(exporter)

app = FastAPI(title="ML Sentiment API")
model = joblib.load('model.pkl')

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
                self.minconn,
                self.maxconn,
                self.database_url
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
                logger.warning("Database unavailable at startup. Will retry on first request.")
                # Start background retry thread
                retry_thread = threading.Thread(target=self._background_retry, daemon=True)
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
            logger.info(f"Retrying database connection (attempt {retry_count}/{max_retries})")
            
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
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id SERIAL PRIMARY KEY,
                        text TEXT,
                        sentiment TEXT,
                        confidence FLOAT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
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
                (text, sentiment, confidence)
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
    
    # Log to Application Insights
    latency_ms = (time.time() - start_time) * 1000
    
    mmap = stats.stats_recorder.new_measurement_map()
    tmap = tag_map_module.TagMap()
    mmap.measure_float_put(prediction_measure, latency_ms)
    mmap.record(tmap)
    
    logger.info(f"Prediction: {prediction}, Confidence: {confidence:.2f}, Latency: {latency_ms:.2f}ms")
    
    return {
        "sentiment": prediction,
        "confidence": float(confidence),
        "latency_ms": latency_ms
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
    checks = {
        "model": False,
        "database": False
    }
    
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
            "timestamp": datetime.now().isoformat()
        }
    
    return {
        "status": "ready",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
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
            cur.execute("""
                SELECT sentiment, COUNT(*) as count
                FROM predictions
                WHERE timestamp > NOW() - INTERVAL '1 hour'
                GROUP BY sentiment
            """)
            results = cur.fetchall()
            
            # Get average confidence
            cur.execute("""
                SELECT AVG(confidence) as avg_confidence
                FROM predictions
                WHERE timestamp > NOW() - INTERVAL '1 hour'
            """)
            avg_conf = cur.fetchone()[0] or 0
            
            metrics_output = "# HELP predictions_total Total number of predictions\n"
            metrics_output += "# TYPE predictions_total counter\n"
            
            for sentiment, count in results:
                metrics_output += f'predictions_total{{sentiment="{sentiment}"}} {count}\n'
            
            metrics_output += "\n# HELP average_confidence Average prediction confidence\n"
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
```

Update `requirements.txt`:

```txt
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
fastapi==0.104.1
uvicorn==0.24.0
joblib==1.3.2
pydantic==2.5.0
psycopg2-binary==2.9.9
opencensus-ext-azure==1.1.9
opencensus-ext-flask==0.8.1
```

### Step 6.4: Rebuild and Deploy with App Insights

```bash
# 1. Store connection string in Key Vault
az keyvault secret set \
  --vault-name $KV_NAME \
  --name "appinsights-connection-string" \
  --value "$CONNECTION_STRING"

# 2. Update SecretProviderClass
cat <<EOF | kubectl apply -f -
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: azure-keyvault-secrets
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "true"
    userAssignedIdentityID: "$AKS_IDENTITY"
    keyvaultName: "$KV_NAME"
    cloudName: ""
    objects: |
      array:
        - |
          objectName: database-url
          objectType: secret
        - |
          objectName: appinsights-connection-string
          objectType: secret
    tenantId: "$TENANT_ID"
  secretObjects:
  - secretName: app-secrets
    type: Opaque
    data:
    - objectName: database-url
      key: database-url
    - objectName: appinsights-connection-string
      key: appinsights-connection-string
EOF

# 3. Update deployment
cat <<EOF | kubectl apply -f -
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
        image: mldemoacr.azurecr.io/ml-api:v3
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: APPLICATIONINSIGHTS_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: appinsights-connection-string
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 15
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
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
EOF

# 4. Rebuild and push image
docker build -t ml-api .
docker tag ml-api mldemoacr.azurecr.io/ml-api:v3
az acr login --name mldemoacr
docker push mldemoacr.azurecr.io/ml-api:v3

# 5. Restart deployment
kubectl rollout restart deployment/ml-api
kubectl rollout status deployment/ml-api

# 6. Test and generate telemetry
for i in {1..20}; do
  curl -X POST http://$INGRESS_IP/predict \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"This is test $i\"}"
  sleep 1
done
```

### Step 6.5: Install Prometheus and Grafana

```bash
# 1. Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# 2. Create monitoring namespace
kubectl create namespace monitoring

# 3. Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# 4. Wait for pods
kubectl get pods -n monitoring -w
# Press Ctrl+C when all are Running

# 5. Expose Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Access at http://localhost:3000
# Default credentials: admin / prom-operator
```

### Step 6.6: Create Custom Grafana Dashboard

Access Grafana at http://localhost:3000

1. Login with `admin` / `prom-operator`
2. Change password when prompted
3. Go to "Dashboards" → "New" → "Import"
4. Use dashboard ID: `315` (Kubernetes cluster monitoring)
5. Click "Load" and "Import"

Create custom dashboard for ML API:

1. Click "+" → "Dashboard"
2. Click "Add visualization"
3. Select "Prometheus" data source
4. Add these queries:

**Query 1 - Request Rate:**
```promql
rate(container_network_receive_bytes_total{pod=~"ml-api.*"}[5m])
```

**Query 2 - CPU Usage:**
```promql
sum(rate(container_cpu_usage_seconds_total{pod=~"ml-api.*"}[5m])) by (pod)
```

**Query 3 - Memory Usage:**
```promql
sum(container_memory_working_set_bytes{pod=~"ml-api.*"}) by (pod)
```

5. Save dashboard as "ML API Metrics"

### Step 6.7: View Application Insights Data

```bash
# Open Application Insights in Azure Portal
az monitor app-insights component show \
  --app ml-demo-insights \
  --resource-group ml-demo-rg \
  --query id -o tsv

echo "Open this in Azure Portal:"
echo "https://portal.azure.com/#@/resource$(az monitor app-insights component show --app ml-demo-insights --resource-group ml-demo-rg --query id -o tsv)/overview"
```

In Application Insights, check:
1. **Live Metrics** - Real-time requests
2. **Failures** - Any errors
3. **Performance** - Request latency
4. **Logs** - Custom log messages

### ✅ Phase 6 Complete Checklist

```bash
echo "=== Phase 6 Verification ==="

# 1. Application Insights receiving data
az monitor app-insights events show \
  --app ml-demo-insights \
  --resource-group ml-demo-rg \
  --type requests \
  --offset 1h

# 2. Container Insights active
kubectl get pods -n kube-system | grep oms

# 3. Prometheus running
kubectl get pods -n monitoring | grep prometheus

# 4. Grafana accessible
kubectl get svc -n monitoring prometheus-grafana

# 5. Custom metrics endpoint working
curl http://$INGRESS_IP/metrics

# 6. Health endpoint (liveness probe)
echo "Liveness probe:"
curl http://$INGRESS_IP/health

# 7. Ready endpoint (readiness probe)
echo "Readiness probe:"
curl http://$INGRESS_IP/ready

echo "✅ Phase 6 Complete!"
echo "Access Grafana: kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
echo "Access Application Insights: Azure Portal"
```

**Time taken:** 2-3 hours

---

## 🔄 PHASE 7: Automated Retraining (Detailed Steps)

**Goal:** Schedule weekly model retraining with Azure Functions

### Step 7.1: Create Storage Account for Models

```bash
# 1. Create storage account
az storage account create \
  --name mlmodelstorage$(date +%s | tail -c 6) \
  --resource-group ml-demo-rg \
  --location eastus \
  --sku Standard_LRS

# Note the storage account name
STORAGE_ACCOUNT="mlmodelstorage123456"  # Replace with actual

# 2. Create container for models
az storage container create \
  --name models \
  --account-name $STORAGE_ACCOUNT

# 3. Create container for training data
az storage container create \
  --name training-data \
  --account-name $STORAGE_ACCOUNT

# 4. Get connection string
STORAGE_CONNECTION=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT \
  --resource-group ml-demo-rg \
  --query connectionString -o tsv)

echo "Storage Connection String: $STORAGE_CONNECTION"
```

### Step 7.2: Create Azure Function App

```bash
# 1. Create Function App (Python 3.9)
az functionapp create \
  --resource-group ml-demo-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name ml-training-func-$(date +%s | tail -c 6) \
  --storage-account $STORAGE_ACCOUNT \
  --os-type Linux

# Note the function app name
FUNCTION_APP="ml-training-func-123456"  # Replace with actual

# 2. Configure app settings
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group ml-demo-rg \
  --settings \
    STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION" \
    DATABASE_URL="postgresql://myadmin:YourPassword123!@ml-demo-db.postgres.database.azure.com/predictions" \
    STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT"
```

### Step 7.3: Create Training Function Code

Create local directory structure:

```bash
mkdir -p azure-function/ModelRetraining
cd azure-function
```

Create `requirements.txt`:
```txt
azure-functions
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
joblib==1.3.2
psycopg2-binary==2.9.9
azure-storage-blob==12.19.0
```

Create `host.json`:
```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

Create `ModelRetraining/__init__.py`:
```python
import logging
import azure.functions as func
import pandas as pd
import psycopg2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from azure.storage.blob import BlobServiceClient
import os
from datetime import datetime
import io

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Model retraining function started')
    
    # Configuration
    DATABASE_URL = os.environ["DATABASE_URL"]
    STORAGE_CONNECTION = os.environ["STORAGE_CONNECTION_STRING"]
    STORAGE_ACCOUNT = os.environ["STORAGE_ACCOUNT_NAME"]
    
    try:
        # 1. Fetch training data from database
        logging.info("Fetching training data from database...")
        conn = psycopg2.connect(DATABASE_URL)
        
        query = """
            SELECT text, sentiment 
            FROM predictions 
            WHERE timestamp > NOW() - INTERVAL '30 days'
            AND text IS NOT NULL 
            AND sentiment IS NOT NULL
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        logging.info(f"Fetched {len(df)} records for training")
        
        if len(df) < 50:
            logging.warning(f"Not enough data for retraining (found {len(df)}, need >= 50)")
            return
        
        # 2. Prepare data
        X = df['text']
        y = df['sentiment']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 3. Train new model
        logging.info("Training new model...")
        model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000)),
            ('classifier', LogisticRegression(max_iter=1000))
        ])
        
        model.fit(X_train, y_train)
        
        # 4. Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logging.info(f"Model accuracy: {accuracy:.4f}")
        logging.info(f"Classification report:\n{classification_report(y_test, y_pred)}")
        
        # 5. Save model to blob storage with version
        logging.info("Saving model to blob storage...")
        blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION)
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"model_{timestamp}.pkl"
        
        # Serialize model to bytes
        model_bytes = io.BytesIO()
        joblib.dump(model, model_bytes)
        model_bytes.seek(0)
        
        # Upload to blob
        blob_client = blob_service_client.get_blob_client(
            container="models",
            blob=model_filename
        )
        blob_client.upload_blob(model_bytes.read(), overwrite=True)
        
        # Also save as "latest"
        blob_client_latest = blob_service_client.get_blob_client(
            container="models",
            blob="model_latest.pkl"
        )
        model_bytes.seek(0)
        blob_client_latest.upload_blob(model_bytes.read(), overwrite=True)
        
        # 6. Save training metadata
        metadata = {
            "timestamp": timestamp,
            "accuracy": accuracy,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "model_filename": model_filename
        }
        
        metadata_str = str(metadata)
        blob_client_meta = blob_service_client.get_blob_client(
            container="models",
            blob=f"metadata_{timestamp}.txt"
        )
        blob_client_meta.upload_blob(metadata_str, overwrite=True)
        
        logging.info(f"Model saved successfully: {model_filename}")
        logging.info(f"Metadata: {metadata}")
        
    except Exception as e:
        logging.error(f"Error during retraining: {str(e)}")
        raise
```

Create `ModelRetraining/function.json`:
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "mytimer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 0 2 * * 0"
    }
  ]
}
```

The schedule `0 0 2 * * 0` means: Every Sunday at 2:00 AM UTC

### Step 7.4: Deploy Function to Azure

```bash
# 1. Install Azure Functions Core Tools (if not already)
# On Linux/Mac:
brew install azure-functions-core-tools@4
# On Windows: Download from Microsoft

# 2. Initialize function app
cd azure-function
func init --worker-runtime python --python

# 3. Deploy to Azure
func azure functionapp publish $FUNCTION_APP --build remote

# Wait for deployment (2-3 minutes)

# 4. Verify deployment
az functionapp function show \
  --name $FUNCTION_APP \
  --resource-group ml-demo-rg \
  --function-name ModelRetraining
```

### Step 7.5: Test the Training Function

```bash
# 1. Trigger function manually (don't wait for Sunday!)
az functionapp function invoke \
  --name $FUNCTION_APP \
  --resource-group ml-demo-rg \
  --function-name ModelRetraining

# 2. Check logs
az functionapp log tail \
  --name $FUNCTION_APP \
  --resource-group ml-demo-rg

# 3. Verify model was saved
az storage blob list \
  --container-name models \
  --account-name $STORAGE_ACCOUNT \
  --output table

# You should see model_YYYYMMDD_HHMMSS.pkl and model_latest.pkl
```

### Step 7.6: Update API to Load Latest Model from Blob

Update `src/api/main.py` to add model loading from blob storage. Add these imports and functions to the existing code:

```python
# Add to existing imports at the top of the file
from azure.storage.blob import BlobServiceClient
import io

# Add storage client configuration after DATABASE_URL
STORAGE_CONNECTION = os.getenv("STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION) if STORAGE_CONNECTION else None

def load_latest_model():
    """Load the latest model from blob storage with fallback to local."""
    try:
        if blob_service_client:
            blob_client = blob_service_client.get_blob_client(
                container="models",
                blob="model_latest.pkl"
            )
            model_bytes = blob_client.download_blob().readall()
            loaded_model = joblib.load(io.BytesIO(model_bytes))
            logger.info("Loaded model from blob storage")
            return loaded_model
        else:
            logger.info("Loading local model (no blob storage configured)")
            return joblib.load('model.pkl')
    except Exception as e:
        logger.error(f"Error loading model from blob: {str(e)}")
        logger.info("Falling back to local model")
        return joblib.load('model.pkl')

# Replace the simple model loading with:
model = load_latest_model()

# Add these new endpoints to the existing API

@app.post("/reload-model")
def reload_model():
    """Reload the latest model from storage."""
    global model
    try:
        model = load_latest_model()
        return {"status": "success", "message": "Model reloaded successfully"}
    except Exception as e:
        logger.error(f"Failed to reload model: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/model-info")
def model_info():
    """Get information about current model."""
    try:
        if blob_service_client:
            blob_client = blob_service_client.get_blob_client(
                container="models",
                blob="model_latest.pkl"
            )
            properties = blob_client.get_blob_properties()
            
            return {
                "model_location": "blob_storage",
                "last_modified": properties.last_modified.isoformat(),
                "size_bytes": properties.size,
                "status": "active"
            }
        else:
            return {
                "model_location": "local_file",
                "status": "active"
            }
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return {"status": "error", "message": str(e)}
```

Update `requirements.txt` to add the Azure Storage dependency:

```txt
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
fastapi==0.104.1
uvicorn==0.24.0
joblib==1.3.2
pydantic==2.5.0
psycopg2-binary==2.9.9
opencensus-ext-azure==1.1.9
opencensus-ext-flask==0.8.1
azure-storage-blob==12.19.0
```

### Step 7.7: Store Storage Connection String in Key Vault

```bash
# 1. Add storage connection string to Key Vault
az keyvault secret set \
  --vault-name $KV_NAME \
  --name "storage-connection-string" \
  --value "$STORAGE_CONNECTION"

# 2. Update SecretProviderClass to include storage secret
cat <<EOF | kubectl apply -f -
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: azure-keyvault-secrets
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "true"
    userAssignedIdentityID: "$AKS_IDENTITY"
    keyvaultName: "$KV_NAME"
    cloudName: ""
    objects: |
      array:
        - |
          objectName: database-url
          objectType: secret
        - |
          objectName: appinsights-connection-string
          objectType: secret
        - |
          objectName: storage-connection-string
          objectType: secret
    tenantId: "$TENANT_ID"
  secretObjects:
  - secretName: app-secrets
    type: Opaque
    data:
    - objectName: database-url
      key: database-url
    - objectName: appinsights-connection-string
      key: appinsights-connection-string
    - objectName: storage-connection-string
      key: storage-connection-string
EOF

# 3. Update deployment with storage connection
cat <<EOF | kubectl apply -f -
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
        - name: APPLICATIONINSIGHTS_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: appinsights-connection-string
        - name: STORAGE_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: storage-connection-string
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 15
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
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
EOF

# 4. Rebuild and deploy
docker build -t ml-api .
docker tag ml-api mldemoacr.azurecr.io/ml-api:v4
docker push mldemoacr.azurecr.io/ml-api:v4

kubectl rollout restart deployment/ml-api
kubectl rollout status deployment/ml-api
```

### Step 7.8: Create Automated Model Reload Mechanism

Create a Kubernetes CronJob to reload model after training:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: model-reload
spec:
  schedule: "15 2 * * 0"  # 15 minutes after training (2:15 AM Sunday)
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: model-reload
            image: curlimages/curl:latest
            command:
            - /bin/sh
            - -c
            - |
              echo "Triggering model reload..."
              curl -X POST http://ml-api-service/reload-model
              echo "Model reload triggered"
          restartPolicy: OnFailure
EOF

# Verify CronJob created
kubectl get cronjobs
```

### Step 7.9: Test End-to-End Retraining Flow

```bash
# 1. Generate some prediction data
echo "Generating prediction data..."
for i in {1..100}; do
  SENTIMENT=$( [ $((RANDOM % 2)) -eq 0 ] && echo "positive" || echo "negative" )
  TEXT="This is a $SENTIMENT test message number $i"
  
  curl -s -X POST http://$INGRESS_IP/predict \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"$TEXT\"}" > /dev/null
  
  [ $((i % 10)) -eq 0 ] && echo "Generated $i predictions..."
done

echo "✅ Generated 100 predictions"

# 2. Manually trigger retraining
echo "Triggering manual retraining..."
az functionapp function invoke \
  --name $FUNCTION_APP \
  --resource-group ml-demo-rg \
  --function-name ModelRetraining

# 3. Wait and check if model was created
sleep 60
az storage blob list \
  --container-name models \
  --account-name $STORAGE_ACCOUNT \
  --query "[?name=='model_latest.pkl'].{Name:name, Modified:properties.lastModified}" \
  --output table

# 4. Manually trigger model reload
kubectl create job --from=cronjob/model-reload manual-reload-$(date +%s)

# 5. Check if reload worked
kubectl logs -l job-name=manual-reload-* --tail=20

# 6. Verify API is using new model
curl http://$INGRESS_IP/health
```

### Step 7.10: Test Model Endpoints

Test the model endpoints that were added in Step 7.6:

```bash
# Rebuild and deploy with all updates
docker build -t ml-api .
docker tag ml-api mldemoacr.azurecr.io/ml-api:v5
docker push mldemoacr.azurecr.io/ml-api:v5
kubectl set image deployment/ml-api ml-api=mldemoacr.azurecr.io/ml-api:v5
kubectl rollout status deployment/ml-api

# Test model info endpoint
curl http://$INGRESS_IP/model-info

# Test model reload endpoint
curl -X POST http://$INGRESS_IP/reload-model

# Verify liveness and readiness probes
curl http://$INGRESS_IP/health
curl http://$INGRESS_IP/ready
```

### ✅ Phase 7 Complete Checklist

```bash
echo "=== Phase 7 Verification ==="

# 1. Storage account has models
echo "1. Models in storage:"
az storage blob list \
  --container-name models \
  --account-name $STORAGE_ACCOUNT \
  --output table

# 2. Function app is deployed
echo "2. Function app status:"
az functionapp show \
  --name $FUNCTION_APP \
  --resource-group ml-demo-rg \
  --query state

# 3. CronJob for model reload exists
echo "3. Model reload CronJob:"
kubectl get cronjobs

# 4. API can load models from blob
echo "4. Model info from API:"
curl http://$INGRESS_IP/model-info | jq

# 5. Check scheduled training
echo "5. Next scheduled training:"
az functionapp function show \
  --name $FUNCTION_APP \
  --resource-group ml-demo-rg \
  --function-name ModelRetraining \
  --query "config.bindings[0].schedule"

echo ""
echo "✅ Phase 7 Complete!"
echo "Model retraining is scheduled for every Sunday at 2:00 AM UTC"
echo "Model will be automatically reloaded at 2:15 AM UTC"
```

**Time taken:** 3-4 hours

---

## 🎉 FINAL VERIFICATION

You've completed all 7 phases! Let's verify everything works:

```bash
#!/bin/bash
echo "==================================="
echo "  FINAL PROJECT VERIFICATION"
echo "==================================="

# Get ingress IP
INGRESS_IP=$(kubectl get ingress ml-api-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo ""
echo "1. Infrastructure"
echo "-----------------"
kubectl get nodes
kubectl get pods -l app=ml-api
kubectl get svc
kubectl get ingress

echo ""
echo "2. Security"
echo "-----------"
echo "Key Vault secrets:"
az keyvault secret list --vault-name $KV_NAME --query "[].name" -o table
echo "Network policies:"
kubectl get networkpolicies

echo ""
echo "3. Monitoring"
echo "-------------"
kubectl get pods -n monitoring | grep -E "prometheus|grafana"
az monitor app-insights component show --app ml-demo-insights --resource-group ml-demo-rg --query name

echo ""
echo "4. ML Pipeline"
echo "--------------"
echo "Storage containers:"
az storage container list --account-name $STORAGE_ACCOUNT --query "[].name" -o table
echo "Function app:"
az functionapp show --name $FUNCTION_APP --resource-group ml-demo-rg --query "name,state"

echo ""
echo "5. API Testing"
echo "--------------"
echo "Liveness probe (health check):"
curl -s http://$INGRESS_IP/health | jq

echo ""
echo "Readiness probe:"
curl -s http://$INGRESS_IP/ready | jq

echo ""
echo "Model info:"
curl -s http://$INGRESS_IP/model-info | jq

echo ""
echo "Prediction test:"
curl -s -X POST http://$INGRESS_IP/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"This project is amazing!"}' | jq

echo ""
echo "Metrics:"
curl -s http://$INGRESS_IP/metrics | head -25

echo ""
echo "==================================="
echo "  ✅ ALL SYSTEMS OPERATIONAL"
echo "==================================="
echo ""
echo "Access points:"
echo "- API: http://$INGRESS_IP"
echo "- Grafana: kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
echo "- Azure Portal: https://portal.azure.com"
echo ""
echo "API Endpoints:"
echo "- POST /predict     - Make sentiment predictions"
echo "- GET  /health      - Liveness probe (app is running)"
echo "- GET  /ready       - Readiness probe (app + DB ready)"
echo "- GET  /metrics     - Prometheus metrics"
echo "- GET  /model-info  - Current model information"
echo "- POST /reload-model - Reload model from blob storage"
echo ""
echo "Next steps:"
echo "1. Add CI/CD pipeline (GitHub Actions)"
echo "2. Implement A/B testing"
echo "3. Add data drift detection"
echo "4. Document your learnings"
echo "5. Add to your resume/portfolio!"
```

---

## 📊 Cost Summary

**Current monthly costs:**
- AKS (1x Standard_B2s): ~$60
- PostgreSQL (Basic): ~$30
- Storage Account: ~$2
- Application Insights: ~$5
- Function App (Consumption): ~$0-5
- Container Registry: ~$5
- Key Vault: ~$1
- Load Balancer: ~$20

**Total: ~$123-128/month**

**Cost savings tips:**
```bash
# Scale down when not using
az aks scale --resource-group ml-demo-rg --name ml-demo-aks --node-count 0

# Stop PostgreSQL
az postgres flexible-server stop --resource-group ml-demo-rg --name ml-demo-db

# Scale back up
az aks scale --resource-group ml-demo-rg --name ml-demo-aks --node-count 1
az postgres flexible-server start --resource-group ml-demo-rg --name ml-demo-db
```

---

## 🎓 What You've Accomplished

You now have production-ready ML infrastructure with:

✅ Containerized ML API running in AKS
✅ Automated retraining pipeline
✅ Comprehensive monitoring and logging
✅ Enterprise-grade security (Key Vault, RBAC, Network Policies)
✅ Infrastructure as Code (Terraform)
✅ Scheduled model updates
✅ Private networking
✅ Scalability (HPA, multiple replicas)
✅ Database connection pooling (ThreadedConnectionPool)
✅ Graceful startup (retries if DB is unavailable)
✅ Error isolation (predictions succeed even if DB fails)
✅ Separate health probes (liveness vs readiness)
