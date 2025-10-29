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