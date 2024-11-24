==写在前面==
containerd和docker类似，命令是crt
<font color="red">本文已弃用</font>
最新参考：[[树莓派配k8s-containerd]]
# 1删除docker，安装依赖库
```bash
#删除旧包，这里不需要
sudo apt-get remove docker docker-engine docker.io containerd runc

# 更新源
sudo apt-get update

# 安装新源
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 下载密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加新源
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
```
# 2安装containerd
## 2.1执行下述命令：
```bash
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# 设置所需的 sysctl 参数，参数在重新启动后保持不变
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

# 应用 sysctl 参数而不重新启动
sudo sysctl --system

# 更新源
sudo apt-get update

# 安装containerd
sudo apt-get install containerd
```
安装完成后,查看containerd服务是否激活

```bash
sudo systemctl status containerd
```
## 2.2配置containerd
用默认配置覆盖原来的配置

```text
containerd config default | sudo tee /etc/containerd/config.toml
```

重新启动 containerd，看起来正常

```text
systemctl restart containerd
```
### 配置systemd为cgroup驱动程序

[kubelet](https://link.zhihu.com/?target=https%3A//kubernetes.io/docs/reference/generated/kubelet)和底层容器运行时(containerd)都需要对接控制组来强制执行[为 Pod 和容器管理资源](https://link.zhihu.com/?target=https%3A//kubernetes.io/zh-cn/docs/concepts/configuration/manage-resources-containers/)并为诸如 CPU、内存这类资源设置请求和限制。若要对接控制组，kubelet 和容器运行时需要使用一个**cgroup 驱动**。 关键的一点是 kubelet 和容器运行时需使用相同的 cgroup 驱动并且采用相同的配置。

在 /etc/containerd/config.toml 中设置

```text
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
  ...
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
    SystemdCgroup = true
```

### 修改默认镜像仓库

在 /etc/containerd/config.toml 中设置

```text
    sandbox_image = "registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.6"
```


### 重载沙箱（pause）镜像

在 `/etc/containerd/config.toml` 中设置：

```text
[plugins."io.containerd.grpc.v1.cri"]
  sandbox_image = "registry.k8s.io/pause:3.2"
```
再次重新启动 containerd：

```text
sudo systemctl daemon-reload 
sudo systemctl restart containerd 
# 查看containerd启动状态 
sudo systemctl status containerd 
# 查看日志 
journalctl -xeu containerd
```

## 2.3安装CNI插件

注意，[http://containerd.io](https://link.zhihu.com/?target=http%3A//containerd.io)包括了`runc`, 但是不包括CNI插件，我们需要[手动安装CNI插件](https://link.zhihu.com/?target=https%3A//github.com/containerd/containerd/blob/main/docs/getting-started.md%23step-3-installing-cni-plugins)：

访问：[Releases · containernetworking/plugins (github.com)](https://link.zhihu.com/?target=https%3A//github.com/containernetworking/plugins/releases)获取最新版本的插件，然后将其安装到`/opt/cni/bin`中：

```bash
$ wget https://github.com/containernetworking/plugins/releases/download/v1.3.0/cni-plugins-linux-amd64-v1.3.0.tgz
$ mkdir -p /opt/cni/bin
$ tar Cxzvf /opt/cni/bin cni-plugins-linux-amd64-v1.3.0.tgz
./
./macvlan
./static
./vlan
./portmap
./host-local
./vrf
./bridge
./tuning
./firewall
./host-device
./sbr
./loopback
./dhcp
./ptp
./ipvlan
./bandwidth
```

# 3安装k8s
安装k8s（阿里好使）
## 3.1安装k8s
```sh-session
swapoff -a关闭分区！！！
apt-get update && apt-get install -y apt-transport-https安装依赖
```
进入root权限输入‘su’
如果是第一次会报错su: Authentication failure，重新设置密码即可
```
sudo passwd root设置su密码（第一次需要）
```


```
添加软件密钥，添加软件更新的源服务器的地址：
curl -s https://mirrors.aliyun.com/kubernetes/apt/doc/apt-key.gpg | apt-key add -
cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb https://mirrors.aliyun.com/kubernetes/apt/ kubernetes-xenial main
EOF
sudo apt-get update更新
apt-get install -y kubelet kubeadm kubectl安装
```
==EORRE如果出现-bash: /etc/apt/sources.list.d/kubernetes.list: Permission denied==报错是因为sources.list.d只有读权限（ls -lhi看权限）需要修改权限chmod或者进入su重新运行。
## 3.2拉取k8s依赖镜像
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


# 参考文献
1[如何在Ubuntu-22上安装Kubernetes(k8s)环境 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/651200897)
2http://t.csdnimg.cn/nI1C9
3[如何用 Kubeadm 在 Debian 11 上安装 Kubernetes 集群 | Linux 中国 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/587922250)