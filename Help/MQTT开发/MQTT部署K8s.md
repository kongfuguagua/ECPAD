==写在前面==
<font color="red">MQTT基于订阅发布机制，包括消息服务器broker和client</font>

>2024.1.21日更新
本文介绍了MQTT容器集群部署和mqtt-mnsit微服务链部署
具体镜像

# 目录
###### 1MQTT集群部署
###### 2MQTT-mnist微服务链部署
###### 3待解决问题

# 1MQTT集群部署
## 1.1MQTT-K8S service文件
该文件生成了两个mqttservice且开放了1883端口，分别endpoint=service：inputserver
```
---
apiVersion: v1
kind: Service
metadata:
  name: mqttbroker001
spec:
  ports:
  - port: 1883
    targetPort: 1883
    name: inputserver
  selector:
    place: worknode001
---
apiVersion: v1
kind: Service
metadata:
  name: mqttbroker002
spec:
  ports:
  - port: 1883
    targetPort: 1883
    name: inputserver
  selector:
    place: worknode002
```
## 1.2 MQTT deployment
由于需要集群组网，每个mosquitto.conf需要修改为bright模式配置。bright 模式只需要1个配置即可。而n个broker修改步骤为：第一个添加n-1个地址，第二个添加n-2个地址，···第n个不需要添加。
```
allow_anonymous true#测试场景允许匿名，如果false需要配置用户名和密码
listener 1883#监听端口号
#持久化配置
persistence true#持久化，数据会保存在broker
persistence_location /mosquitto/data#数据保存路径
log_dest file /mosquitto/log/mosquitto.log#日志保存路径
#bright配置
connection broker002#目标机名
address 10.102.182.96:1883#目标IP和port
topic # both 2#所有topic的双向通信
```
之后k8s部署
```
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vol-mosquitto
  labels:
    app: vol-pod1
    place: worknode001
spec:
  selector:
    matchLabels:
      app: vol-pod1
      place: worknode001
  replicas: 1
  template:
    metadata:
      labels:
        app: vol-pod1
        place: worknode001
    spec:
      nodeName: worknode001#指定部署节点
      containers:
        - name: mosquitto
          image: eclipse-mosquitto
          ports:
            - containerPort: 1883
          volumeMounts:
            - name: vol-mosquitto
              mountPath: /mosquitto # 容器的数据目录
      volumes:   # volumes和container处于同一层级，别搞错了
        - name:  vol-mosquitto
          hostPath:
            path:  /mosquitto  # 宿主机目录
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vol-mosquitto-2
  labels:
    app: vol-pod2
    place: worknode002
spec:
  selector:
    matchLabels:
      app: vol-pod2
      place: worknode002
  replicas: 1
  template:
    metadata:
      labels:
        app: vol-pod2
        place: worknode002
    spec:
      nodeName: worknode002
      containers:
        - name: mosquitto
          image: eclipse-mosquitto
          ports:
            - containerPort: 1883
          volumeMounts:
            - name: vol-mosquitto
              mountPath: /mosquitto # 容器的数据目录
      volumes:   # volumes和container处于同一层级，别搞错了
        - name:  vol-mosquitto
          hostPath:
            path:  /mosquitto  # 宿主机目录
---

```
# 2MQTT-mnist微服务链部署
部署文件为
```
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: mnistinput
  name: mnistinput-1
spec:
  selector:
    matchLabels:
      app: mnistinput
  replicas: 1
  template:
    metadata:
      labels:
        app: mnistinput
    spec:
      containers:
      - image:  registry.cn-hangzhou.aliyuncs.com/mnist-infer/mqtt-mnist-input:v1.0.0
        name: mnistinput-dome1
        ports:
        - containerPort: 1883
        command: ["python","main.py"]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: mnistinfer
    env: inference
  name: mnistinfer-1
spec:
  selector:
    matchLabels:
      app: mnistinfer
      env: inference
  replicas: 1
  template:
    metadata:
      labels:
        app: mnistinfer
        env: inference
    spec:
      containers:
      - image:  registry.cn-hangzhou.aliyuncs.com/mnist-infer/mqtt-mnist-infer:v1.0.0
        name: mnistinfer-dome1
        ports:
        - containerPort: 1883
        command: ["python","main.py"]
---
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
      - image:  registry.cn-hangzhou.aliyuncs.com/mnist-infer/mqtt-mnist-output:v1.0.0
        name: mnistoutput-dome1
        ports:
        - containerPort: 1883
        command: ["python","main.py"]
```
# 3问题
## 1mqtt组网需要手动配置，需要查n个mqtt-services的ip，并填入mosquitto.conf文件。而且必须先创建service后创建pod
## 2mnist-app与哪个broker链接在封装的时候固定住，但可以使用python main.py --ip=[]注入ip，在deployment文件指定启动指令即可，但仍需要手动查询并指定broker ip。
