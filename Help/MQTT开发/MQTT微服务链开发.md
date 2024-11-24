==写在前面==
<font color="red">MQTT基于订阅发布机制，包括消息服务器broker和client</font>

>2024.1.21日更新
本文介绍了MQTT容器化的配置和mqtt-mnsit镜像使用方法
具体镜像
```
docker pull registry.cn-hangzhou.aliyuncs.com/mnist-infer/mqtt-mnist-input:v0.1.0
docker pull registry.cn-hangzhou.aliyuncs.com/mnist-infer/mqtt-mnist-infer:v0.0.1
docker pull registry.cn-hangzhou.aliyuncs.com/mnist-infer/mqtt-mnist-output:v0.0.1
```

# 目录
###### 1mosquitto容器化配置
###### 2mqtt-mnsit
###### 3demo
# 1mosquitto容器化配置

## 1.1 挂载配置
容器化mosquitto的log文件挂在容器内部卷，而容器出现问题后log文件被销毁，无法debug。log需要挂载在宿主机。下述为宿主机配置脚本
```
#!/bin/bash
mkdir -p /mosquitto/config
mkdir -p /mosquitto/data
mkdir -p /mosquitto/log
cat > /mosquitto/config/mosquitto.conf<<EOF
allow_anonymous true
listener 1883
persistence true
persistence_location /mosquitto/data
log_dest file /mosquitto/log/mosquitto.log
EOF
chmod -R 755 /mosquitto
chmod -R 777 /mosquitto/log
```
## 1.2容器化mosquitto.conf配置
```
allow_anonymous true#测试场景允许匿名，如果false需要配置用户名和密码
listener 1883#监听端口号
#持久化配置
persistence true#持久化，数据会保存在broker
persistence_location /mosquitto/data#数据保存路径
log_dest file /mosquitto/log/mosquitto.log#日志保存路径
```
## 1.3mosquitto容器启动指令
```
sudo docker pull eclipse-mosquitto:latest #-可加-platform
sudo docker run -it --name=mosquitto --privileged \
-p 1883:1883 -p 9001:9001 \
-v /mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf \
-v /mosquitto/data:/mosquitto/data \
-v /mosquitto/log:/mosquitto/log \
--rm eclipse-mosquitto
```
# 2mqtt-mnsit
docker的mqtt客户端要想访问docker的broker需要暴露端口，而宿主机的1883已经被broker占领
```
sudo docker run --rm -it -p 1884:1883 registry.cn-hangzhou.aliyuncs.com/mnist-infer/mqtt-mnist-infer:v0.0.1 bash
```
进入容器内部执行,docker ip为docker虚拟网卡ip，使用ip a查询。port与上述指令-p a:b的b相同
```
python main.py --ip=[docker ip] --port=[1883]
```
# 3demo
mnist的案例，按顺序执行即可
开4个终端，分别执行
终端1启动mosquito
```
sudo docker run -it --name=mosquitto --privileged \
-p 1883:1883 -p 9001:9001 \
-v /mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf \
-v /mosquitto/data:/mosquitto/data \
-v /mosquitto/log:/mosquitto/log \
--rm eclipse-mosquitto
```
终端2启动mnist-input
```
sudo docker run --rm -it -p 18884:1883 registry.cn-hangzhou.aliyuncs.com/mnist-infer/mqtt-mnist-input:v0.1.0 bash
python main.py --ip=172.17.0.1
```
终端3启动mnist-infer
```
sudo docker run --rm -it -p 18883:1883 registry.cn-hangzhou.aliyuncs.com/mnist-infer/mqtt-mnist-infer:v0.0.1 bash
python main.py --subip=172.17.0.1
```
终端4启动mnist-output
```
sudo docker run --rm -it -p 18884:1883 registry.cn-hangzhou.aliyuncs.com/mnist-infer/mqtt-mnist-output:v0.0.1 bash
python main.py --ip=172.17.0.1
```