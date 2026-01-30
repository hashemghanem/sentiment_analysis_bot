# Questions
### In the following command, what is the purpose of the `--enable-managed-identity`  and the ssh keys flag?
```bash
az aks create \
  --resource-group ml-demo-rg \
  --name ml-demo-aks \
  --node-count 1 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys \
  --attach-acr mldemoacr
```


### In the following dep manifest, why label is needed both in metadata? also what is the fonction of readinessProbe?
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-api
  labels:
    app: ml-api
spec:
  replicas:1
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
        image: deletemedeleteacr.azurecr.io/ml-api:v1
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
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
```
### How the postgresql is connected to the AKS, and how the secret is passed and then perceived inside the main.py file through the os.getenv("DATABASE_URL")?

### Remove storage you created for terraform state whose name is mldemotfstate
### try to upgrade azuerm to ~>4 and see in terraform.
### i just created terraform but infras were already created, is there a way to create the state based on that?

### Networking Challenge: Connecting AKS to PostgreSQL
**If you used Kubenet in Phase 1:**
- PostgreSQL needs a public endpoint OR firewall rule for AKS node IPs
- Less secure, but works for learning
**If you used Azure CNI + VNet in Phase 1:**
- Can use service endpoints or private endpoints
- More secure, production-ready
### is there a way to automate the ingress installation with helm in terraform or in the aks manifest itself?

### Can you explain me the flow of a request from the user to the API in terms of layers/protocols used? for example:
⚙️ TCP
    
    ↓

📦 HTTP

    ↓

🚦 NGINX (receives traffic, routes it)

    ↓
🎫 Ingress (in Kubernetes: defines routing rules)

    ↓
🧭 API (your application)

    ↓
🌱 REST (how your API is designed)

### see how then nginx sends the request to the right pod in the cluster? is it through a clusterip service or through the ingress itself?

### annotations in ingress manifest under metadata, what are they for?

### what is an app gateway?
### AD vs RBAC vs service principal vs system assigned managed identity?
```
parameters:
    usePodIdentity: "false"                  # Not using old pod identity
    useVMManagedIdentity: "true"             # Use managed identity on VMs
    userAssignedIdentityID: "615d90f8-..."    # Specific user-assigned managed identity ID (not system-assigned)
```

### how to automate roles assignment to: 1)  for the managed identity in terraform? (COMING from the csi add-on) 2) for ad users in terraform to access the aks cluster? (coming from step 5.7 ClusterRole, ClusterRoleBinding, AD Group) 3) for the ci/cd pipeline to access the acr and aks? (coming from step 5.7 ServiceAccount, RoleBinding, Role)

### path of a packet when sending it from a pod to another pod in another node in the same cluster?

### put the clusterrole and clusterrolebinding in manifest files instead, also put the AD group creation in a terraform manifest file if possible?
### why the pain of installing the add-on of azure monitor and application insights when we push the connection string in the main.py file is enough to send the logs to app insights?
### ready and healthy probes difference?
### add to detailed_implementation.md after step 6.3 (monitor and application insight part) the commands to see the logs in app insights from the cli, also the commands to verify good connection to database and number of predictions stored in db from the cli.

### used commands
```bash
az aks get-credentials \
  --resource-group rg-glb-Training_Employees \
  --name ml-demo-aks \
  --overwrite-existing


  KV_NAME='ml-demo-kv-1766162936'
  secretname1='database-url'
  secretname2='appinsights-connection-string'
  az keyvault secret show --vault-name $KV_NAME --name $secretname2 --query value  -o tsv


  az acr build --registry deletemedeleteacr --image ml-api:v4 .

az acr repository list --name deletemedeleteacr --output table

az acr repository show-tags --name deletemedeleteacr --repository ml-api --output table

kubectl get secret app-secrets -o jsonpath="{.data}" | jq 'to_entries[] | {key: .key, value: (.value | @base64d)}'

Ingress_IP="9.163.231.146"

kubectl exec -it ml-api-5dbb8b7897-ptv9p -- python -c '
import os
DATABASE_URL = os.getenv("DATABASE_URL")
print("url:", DATABASE_URL)
'
database-url='postgresql://myadmin:MyDemoPassword2026@ml-demo-db.postgres.database.azure.com/predictions?sslmode=require'

DB_SERVER="ml-demo-db"
DB_NAME="predictions"
DB_ADMIN="myadmin"
DB_PASSWORD='MyDemoPassword2026'
echo "6. Total predictions in database:"
az postgres flexible-server execute \
  --name $DB_SERVER \
  --admin-user $DB_ADMIN \
  --admin-password "$DB_PASSWORD" \
  --database-name $DB_NAME \
  --querytext "SELECT COUNT(*) as total_predictions FROM predictions;"
echo ""

echo "7. Recent predictions (last 5):"
az postgres flexible-server execute \
  --name $DB_SERVER \
  --admin-user $DB_ADMIN \
  --admin-password "$DB_PASSWORD" \
  --database-name $DB_NAME \
  --querytext "SELECT id, text, sentiment, confidence, timestamp FROM predictions ORDER BY timestamp DESC LIMIT 5;"
echo ""


APP_INSIGHTS_NAME="ml-demo-insights"
echo ""
echo "=== Verifying Application Insights Integration ==="
echo ""

# Check if Application Insights is receiving data
echo "11. Recent requests in Application Insights:"
az monitor app-insights events show \
  --app $APP_INSIGHTS_NAME \
  --resource-group rg-glb-Training_Employees \
  --type requests \
  --offset 1h \
  --query "[].{Timestamp:timestamp, Name:request.name, ResultCode:request.resultCode, Duration:request.duration}" \
  --output table
echo ""




  ```