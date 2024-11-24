```
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: mnistoutput
    env: output
  name: mnistoutput-1
spec:
  selector:
    matchLabels:
      app: mnistoutput
      env: output
  replicas: 1
  template:
    metadata:
      labels:
        app: mnistoutput
        env: output
    spec:
      containers:
      - image:  registry.cn-hangzhou.aliyuncs.com/mnist-infer/mnist-infer-conduct:v2.0.1
        name: mnistoutput-dome1
        ports:
        - containerPort: 1800
        command: [ "/bin/sh", "-c", "env" ]
        env:
        - name: MY_POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        command: ["sleep"]
        args: ["infinity"]
```