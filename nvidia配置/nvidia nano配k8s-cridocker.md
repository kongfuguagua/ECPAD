==写在前面==
<font color="red">nvidia官方镜像烧录可能会失败</font>

>2024.3.11日更新
本文对NVIDIA系列ARM进行系统烧录、cri-dockerd安装、k8s安装、master节点初始化。
环境配置版本：==cri-docker=0.3.11 ==,==kubeadm kubeclt kubelet=v1.28.2==
><font color="red">配置进行中可能会出现一些如，Not superuser、的权限问题，切换到root即可解决。文件权限问题使用 ls -ihl查看，chmod修改.</font>
>截至2024.3.11日k8s阿里源可以使用

# 目录
###### 1安装操作系统
###### 2修改docker及其配置
###### 3安装cri-dockerd（github）
###### 4安装k8s（阿里好使）
###### 5master初始化

# 1安装操作系统
## 1.1操作系统安装
进入[Jetson Software Getting Started | NVIDIA Developer](https://developer.nvidia.com/embedded/learn/getting-started-jetson)选择对应设备，下载相应镜像。
参考CSDN：Jetson 系列——nvidia jetson xavier nx重新烧录系统
# 2修改docker及其配置
3.2.2换仓库源
在/etc/docker/daemon.json中添加语句

```sh-session
{
"registry-mirrors": ["https://svph38nh.mirror.aliyuncs.com"],
"exec-opts": ["native.cgroupdriver=systemd"]
}
```
==这个是韩梦琦自己申请的阿里云仓库账号。后续毕业可能有变动，建议后续更换为实验室申请账号==
重启docker

```sh-session
sudo systemctl daemon-reload
sudo systemctl restart docker
```
<font color="red">注意.</font>
如果重启失败显示
Job for docker.service failed because the control process exited with error code.
See "systemctl status docker.service" and "journalctl -xe" for details.
说明/etc/docker/daemon.json格式有问题，请自行查找。
# 3安装cri-dockerd（github）
## 3.1克隆cri-docker

```
wget https://github.com/Mirantis/cri-dockerd/releases/download/v0.3.11/cri-dockerd-0.3.11.arm64.tgz
tar zxf cri-dockerd-0.3.11.arm64.tgz
sudo cp cri-dockerd/cri-dockerd /usr/bin/
```
## 3.2修改配置

下载启动文件https://github.com/Mirantis/cri-dockerd/tree/master/packaging/systemd
启动文件放在/usr/lib/systemd/system/下面
修改/usr/lib/systemd/system/cri-docker.service
配置ExecStart=/usr/local/bin/cri-dockerd --container-runtime-endpoint fd:// --network-plugin=cni --pod-infra-container-image=registry.aliyuncs.com/google_containers/pause:3.9
启动cri-docker并设置开机自动启动
```
sudo systemctl daemon-reload
sudo systemctl enable cri-docker --now
```
查看启动状态
systemctl is-active cri-docker

# 4安装k8s（阿里好使）

## 4.1换源和密钥

```sh-session
swapoff -a关闭分区！！！
apt-get update && apt-get install -y apt-transport-https安装依赖
```
进入root权限输入‘su’
如果是第一次会报错su: Authentication failure，重新设置密码即可
```
sudo passwd root设置su密码（第一次需要）
```
添加软件密钥，添加软件更新的源服务器的地址：
```
curl -s https://mirrors.aliyun.com/kubernetes/apt/doc/apt-key.gpg | apt-key add -
cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb https://mirrors.aliyun.com/kubernetes/apt/ kubernetes-xenial main
EOF
sudo apt-get update更新
```
==EORRE如果出现-bash: /etc/apt/sources.list.d/kubernetes.list: Permission denied==报错是因为sources.list.d只有读权限（ls -lhi看权限）需要修改权限chmod或者进入su重新运行。
## 4.2安装k8s
apt安装的kubelet kubectl 和kubeadm版本未必一致，一般安装k8s这三个组件一定要指定版本号，否则apt拉取最新版本可能会出现小版本错误，参考命令如下：
```
sudo apt-cache madison kubeadm 查看可用的版本
sudo apt install kubelet=1.28.2-00 kubectl=1.28.2-00 kubeadm=1.28.2-00
```
## 4.3修改init启动配置文件(可不用，这里可能有bug)
kubelet的cgroup管理员也要用systemd，debian或者ubuntu版本不像centos有kubelet的配置config文件，就得走初始化配置文件来配，所以kubeadm config print init-default > kubeadm-config.yaml
得到初始化配置文件，再新增以下kubelet配置内容：

```
修改
localAPIEndpoint:
  advertiseAddress: 10.180.177.21 #你的ip地址
修改
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers #镜像库
serviceSubnet后加上
podSubnet: 10.244.0.0/16
末尾加上
---
kind: KubeletConfiguration
apiVersion: kubelet.config.k8s.io/v1beta1
cgroupDriver: systemd
```
```
完整文件
apiVersion: kubeadm.k8s.io/v1beta3
bootstrapTokens:
- groups:
  - system:bootstrappers:kubeadm:default-node-token
  token: abcdef.0123456789abcdef
  ttl: 24h0m0s
  usages:
  - signing
  - authentication
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: 0.0.0.0
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///var/run/cri-dockerd.sock
  imagePullPolicy: IfNotPresent
  name: nvidia004
  taints: null
---
apiServer:
  timeoutForControlPlane: 4m0s
apiVersion: kubeadm.k8s.io/v1beta3
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controllerManager: {}
dns: {}
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers
kind: ClusterConfiguration
kubernetesVersion: 1.28.2
networking:
  dnsDomain: cluster.local
  serviceSubnet: 10.96.0.0/12
  podSubnet: 10.244.0.0/16
scheduler: {}
---
kind: KubeletConfiguration
apiVersion: kubelet.config.k8s.io/v1beta1
cgroupDriver: systemd
```
## 4.4拉取k8s依赖镜像(可不用)
kubeadm config images list查看需要什么镜像
自动指定源拉取（我没成功）
```sh-session
kubeadm config images pull \
--image-repository registry.aliyuncs.com/google_containers \
--kubernetes-version v1.18.5
```
写一个脚本完成
新建一个pull_replace.sh文件
```sh-session
#!/bin/bash
# 获取要拉取的镜像信息，images.txt是临时文件
kubeadm config images list > images.txt
# 替换成mirrorgcrio的仓库，该仓库国内可用，和k8s.gcr.io的更新时间只差一两天
sed -i 's@registry.k8s.io@registry.cn-hangzhou.aliyuncs.com/google_containers@g' images.txt
# 拉取各镜像,这里coredns路径有问题得手动调整或者最后加几条
cat images.txt | while read line
do
    sudo docker pull $line
done
# 修改镜像tag为k8s.gcr.io仓库，并删除mirrorgcrio的tag
sed -i 's@registry.cn-hangzhou.aliyuncs.com/google_containers/@@g' images.txt
cat images.txt | while read line
do
    sudo docker tag registry.cn-hangzhou.aliyuncs.com/google_containers/$line registry.k8s.io/$line#registry.k8s.io
    sudo docker rmi -f registry.cn-hangzhou.aliyuncs.com/google_containers/$line
done
#coredns调整语句
sudo docker pull registry.cn-hangzhou.aliyuncs.com/google_containers/coredns:v1.10.1
sudo docker tag registry.cn-hangzhou.aliyuncs.com/google_containers/coredns:v1.10.1 registry.k8s.io/coredns/coredns:v1.10.1 #k8s.gcr.io
sudo docker rmi -f registry.cn-hangzhou.aliyuncs.com/google_containers/coredns:v1.10.1
# 操作完后显示本地docker镜像
sudo docker images
# 删除临时文件
sudo rm -f images.txt
```
运行并打印信息 sh pull_replace.sh | tee output.log
# 5master初始化
<font color="red">检查是否关闭分区！！！</font>
```
free
swapoff -a
```
## 5.1集群初始化
```
sudo kubeadm init --config kubeadm-config.yaml
```
## 5.2集群解散
```
sudo kubeadm reset -f --cri-socket unix:///var/run/cri-dockerd.sock
sudo rm -rf /etc/kubernetes/ && sudo rm -rf /etc/cni && sudo rm -rf /var/lib/kubelet && sudo rm -rf /var/lib/etcd
```