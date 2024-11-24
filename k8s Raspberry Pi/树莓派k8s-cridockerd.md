==写在前面==
<font color="red">每个jccount账号只能登录10个设备.</font>
[Obsidian中文手册](https://publish.obsidian.md/help-zh)

>2023.10.1日更新
本文对树莓派4B进行系统安装、docker安装、cri-dockerd安装、k8s安装、master节点初始化。
环境配置版本：==docker:20.10.5+==，==cri-docker:0.3.4==,==kubeadm kubeclt kubelet:v1.28.2==
><font color="red">配置进行中可能会出现一些如，Not superuser、的权限问题，切换到root即可解决。文件权限问题使用 ls -ihl查看，chmod修改.</font>
>截至2023年10月3日树莓派清华源、docker及k8s阿里源可以使用

k8s自从1.24版本后与docker解构，如在kubeadm init阶段实在过不去有三种方法可以解决：
- 降级k8s到1.20（不推荐）
优点：配置简单
缺点：docker版本不能太高；更新后难以维护
- 配置docker -> cri-dockerd ->k8s体系（==本文使用==）
优点：兼容docker和k8s；对开发者友好（可少学点新东西）
缺点：工程链长，bug不好定位；更新可能存在滞后（滞后时bug没法调）；性能有一定影响
- 配置containrd -> k8s体系[[树莓派配k8s-containerd]]
优点：调用链短；官方支持；版本兼容问题少
缺点：docker转有成本


# 目录
###### 1安装操作系统
###### 2换树莓派更新源（清华好使）
###### 3安装docker（阿里好使）
###### 4安装cri-dockerd（go编译）
###### 5安装k8s（阿里好使）
###### 6master初始化
## 附录
###### 1一键换源.sh文件

# 1安装操作系统
## 1.1树莓派操作系统安装Debian 11 bullseye
https://downloads.raspberrypi.org/imager/imager_latest.exe
下载后选择RaspberryPi OS(64-bit)系统
进入高级设置
设置主机名，useername这个重要决定了远程登录名
![[Pasted image 20231003210535.png]]
烧录后复制wpa_supplicant.conf进boot盘可自动上网
示范sjtu配置
```
country=CN
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
# ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=wheel
network={
ssid="SJTU"
scan_ssid=1
key_mgmt=WPA-EAP
eap=PEAP
identity="交我办账号"
password="交我办密码"
ca_cert="/etc/ssl/certs/Go_Daddy_Root_Certificate_Authority_-_G2.pem"
phase1="peaplabel=0"
phase2="auth=MSCHAPV2"
# subject_match="/CN=radius.net.sjtu.edu.cn"
altsubject_match="DNS:radius.net.sjtu.edu.cn"
# domain_match="radius.net.sjtu.edu.cn" # require v2.4
}
```
示范一般wifi配置
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=CN
 
network={
	ssid="1234567"    #WiFi账号
	psk="123456789"   #WiFi密码
}
```
## 1.2获取ip地址并SSH
进入终端查ip -a，无线网ip为wlan0的ip
在远程登录软件上分别输入 IP地址、主机名，即可远程登录
![[Pasted image 20231003210826.png]]
## 1.3 参考链接
[树莓派系统安装及使用（详细步骤）](http://t.csdnimg.cn/VzlyO)
[树莓派(Raspberry pi) 使用Pi Imager安装烧录操作系统](http://t.csdnimg.cn/7CJ5Q)

#  2换树莓派更新源（清华好使）
进入sudo vi /etc/apt/sources.list
注释掉所有，换成
```sh-session
deb https://mirrors.tuna.tsinghua.edu.cn/debian bullseye main contrib non-free
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bullseye-security main contrib non-free 
deb https://mirrors.tuna.tsinghua.edu.cn/debian bullseye-updates main contrib non-free
```
进入sudo vi /etc/apt/sources.list.d/raspi.list
注释掉所有，换成
```sh-session
deb https://mirrors.tuna.tsinghua.edu.cn/raspberrypi bullseye main
```
# 3安装docker（阿里好使）
## 3.1关闭防火墙和分区和selinux（一般是关的）
```sh-session
swapoff -a#关闭分区！！！
systemctl stop firewalld
systemctl disable firewalld
asus@raspberrypi:~ $ setenforce 0
cat /etc/selinux/config
asus@raspberrypi:~ $ SELINUX=disabled
```
## 3.2安装docker
### 3.2.1如果清华源已经配好了就直接apt安装
```sh-session
sudo apt-get update
sudo apt-get install docker.io
```
### 3.2.2换仓库源
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


# 4安装cri-dockerd（go编译）
## 4.1克隆cri-docker
git clone https://github.com/Mirantis/cri-dockerd.git
## 4.2安装go环境并编译cri-docker
因为cri-dockerd需要go语言编译，所以需要安装go，介绍两种方法，注意go版本需要跟系统一样
1. apt（Debian才行）
sudo apt-get install golang-go 需要指定版本号，后续还要添加GOPATH！麻烦
2. 镜像
docker pull golang:1.21-bullseye 根据Debian版本不同修改
```sh-session
docker pull golang:1.21-bullseye
docker run -it --rm -v $PWD/cri-dockerd:/usr/src/cri-dockerd -w /usr/src/cri-dockerd golang:1.21-bullseye 
mkdir bin
go build -o bin/cri-dockerd
```
解释一下-it是产生一个伪终端口，-rm是用完销毁，-v是挂载卷，-w是容器内工作目录。==这里最要注意的是$PWD/cri-dockerd应该是编译后期待二进制文件放的地方==
## 4.3其余指令，在su下运行
```sh-session
cd cri-dockerd
mkdir -p /usr/local/bin
install -o root -g root -m 0755 cri-dockerd /usr/local/bin/cri-dockerd
install packaging/systemd/* /etc/systemd/system
sed -i -e 's,/usr/bin/cri-dockerd,/usr/local/bin/cri-dockerd,' /etc/systemd/system/cri-docker.service
systemctl daemon-reload
systemctl enable --now cri-docker.socket
```
安装结束
/etc/systemd/system/cri-docker.service
配置ExecStart=/usr/local/bin/cri-dockerd --container-runtime-endpoint fd:// --network-plugin=cni --pod-infra-container-image=registry.aliyuncs.com/google_containers/
# 5安装k8s（阿里好使）
## 5.1修改系统文件
树莓派本身没启动croupmemory，需要在boot配置里修改成如下内容
```
sudo vi /boot/cmdline.txt
加入cgroup_enable=memory cgroup_memory=1
如（不能直接复制，因为每个机器的root=PARTUUID不一样）：
console=serial0,115200 console=tty1 root=PARTUUID=0b9ed906-02 rootfstype=ext4 fsck.repair=yes cgroup_enable=memory cgroup_memory=1 rootwait quiet splash plymouth.ignore-serial-consoles
```
保存后重启
## 5.2安装k8s
### 5.2.1换源和密钥
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
### 5.2.2安装k8s
apt安装的kubelet kubectl 和kubeadm版本未必一致，一般安装k8s这三个组件一定要指定版本号，否则apt拉取最新版本可能会出现小版本错误，参考命令如下：
```
sudo apt-cache madison kubeadm 查看可用的版本
sudo apt install kubelet=1.28.2-00 kubectl=1.28.2-00 kubeadm=1.28.2-00
```
## 5.3修改init启动配置文件(可不用，这里可能有bug)
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
###### 整体kubeadm-config.yaml文档示例
```
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
  advertiseAddress: 10.180.177.21
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///var/run/containerd/containerd.sock
  imagePullPolicy: IfNotPresent
  name: worknode001
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
## 5.4拉取k8s依赖镜像(可不用)
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
# 6master初始化
<font color="red">检查是否关闭分区！！！</font>
```
free
swapoff -a
```
## 6.1集群初始化
```
sudo kubeadm init --config kubeadm-config.yaml
```

## 6.2集群解散
```
sudo kubeadm reset -f
sudo rm -rf /etc/kubernetes/ && sudo rm -rf /etc/cni && sudo rm -rf /var/lib/kubelet && sudo rm -rf /var/lib/etcd
```

# 附录
## 1换源.sh文件
