# 1debug容器内程序
# 2dubug镜像能否运行
# 3debug镜像在k8s集群能否运行
## 3.1进入k8s容器内部
预先设置deployment.yaml文件加入
```
command: ["sleep"]
args: ["infinity"]
```
 例如：
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
apply pod后
```
kubectl get pod
选择要进入的pod
kubectl exec -it pod名 bash
```
开始debug