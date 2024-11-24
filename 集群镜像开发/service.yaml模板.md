```
apiVersion: v1
kind: Service
metadata:
  name: inference
spec:
  ports:
  - port: 1900
    targetPort: 1900
    name: inputserver
  selector:
    env: inference
```