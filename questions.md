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
