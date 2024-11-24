==写在前面==
<font color="red">每个jccount账号只能登录10个设备.</font>
<font color="red">出现bug需要重启时，先重启containerd后重启kubelet.</font>

>2023.10.11日更新
本文对树莓派4B进行系统安装、cri-containerd安装、k8s安装、master节点初始化。
环境配置版本：==cri-containerd:v1.6.24 ==,==kubeadm kubeclt kubelet:v1.28.2==
><font color="red">配置进行中可能会出现一些如，Not superuser、的权限问题，切换到root即可解决。文件权限问题使用 ls -ihl查看，chmod修改.</font>
>截至2023年10月11日树莓派清华源、k8s阿里源可以使用

k8s自从1.24版本后与docker解构，如在kubeadm init阶段实在过不去有三种方法可以解决：
- 降级k8s到1.20（不推荐）
优点：配置简单
缺点：docker版本不能太高；更新后难以维护
- 配置docker -> cri-dockerd ->k8s体系[[树莓派k8s-cridockerd]]
优点：兼容docker和k8s；对开发者友好（可少学点新东西）
缺点：工程链长，bug不好定位；更新可能存在滞后（滞后时bug没法调）；性能有一定影响
- 配置containrd -> k8s体系（==本文使用==）
优点：调用链短；官方支持；版本兼容问题少
缺点：docker转有成本
# 目录
###### 1安装操作系统
###### 2换树莓派更新源（清华好使）
###### 3安装cri-containerd（github）
###### 4安装k8s（阿里好使）
###### 5master初始化

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
更新源
```
sudo apt-get update
```
# 3 安装cri-containerd（github）
containerd要装全，建议从他的github上下源码装，cri-containerd得有，这是k8s与containerd的连接口
```
#删除旧包，这里不需要
sudo apt-get remove docker docker-engine docker.io containerd runc

# 更新源
sudo apt-get update

# 安装依赖
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```
设置所需的 sysctl 参数，参数在重新启动后保持不变
```
sudo vi /etc/modules-load.d/k8s.conf
overlay
br_netfilter


sudo modprobe overlay&&sudo modprobe br_netfilter

# 设置所需的 sysctl 参数，参数在重新启动后保持不变
sudo vi /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
vm.swappiness=0
# 应用 sysctl 参数而不重新启动
sudo sysctl --system

```
## 3.1git及解压
切换目录
```
sudo mkdir -p /etc/kubernets
cd /etc/kubernets
```
下载并解压。后续可能会版本升级，选择linux-arm64即可
```
wget https://github.com/containerd/containerd/releases/download/v1.6.24/cri-containerd-1.6.24-linux-arm64.tar.gz
sudo tar -zxf cri-containerd-1.6.24-linux-arm64.tar.gz
```
移动文件，在路径/etc/kubernets下
```
# 可以查看以下复制的相关文件内容，大概就明白什么意思了 
sudo cp ./etc/crictl.yaml /etc/ 
sudo cp ./etc/systemd/system/containerd.service /etc/systemd/system/
sudo cp ./usr/local/bin/. /usr/local/bin/ -a
sudo cp ./usr/local/sbin/. /usr/local/sbin/ -a
```
## 3.2生成和配置启动文件
```
mkdir -p /etc/containerd #创建文件夹  
containerd config default > /etc/containerd/config.toml #生成配置文件
```
containerd的配置文件中，sandboximage的版本要符合当前k8s组件版本，比如k8s是1.28，则pause为3.9版本；同时要把systemdCgroup改为true，我们用systemd管理cgroup
```
修改为
sandbox_image = "registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.9"
···
SystemdCgroup = true

```
##### 示例
```
disabled_plugins = []
imports = []
oom_score = 0
plugin_dir = ""
required_plugins = []
root = "/var/lib/containerd"
state = "/run/containerd"
temp = ""
version = 2

[cgroup]
  path = ""

[debug]
  address = ""
  format = ""
  gid = 0
  level = ""
  uid = 0

[grpc]
  address = "/run/containerd/containerd.sock"
  gid = 0
  max_recv_message_size = 16777216
  max_send_message_size = 16777216
  tcp_address = ""
  tcp_tls_ca = ""
  tcp_tls_cert = ""
  tcp_tls_key = ""
  uid = 0

[metrics]
  address = ""
  grpc_histogram = false

[plugins]

  [plugins."io.containerd.gc.v1.scheduler"]
    deletion_threshold = 0
    mutation_threshold = 100
    pause_threshold = 0.02
    schedule_delay = "0s"
    startup_delay = "100ms"

  [plugins."io.containerd.grpc.v1.cri"]
    device_ownership_from_security_context = false
    disable_apparmor = false
    disable_cgroup = false
    disable_hugetlb_controller = true
    disable_proc_mount = false
    disable_tcp_service = true
    enable_selinux = false
    enable_tls_streaming = false
    enable_unprivileged_icmp = false
    enable_unprivileged_ports = false
    ignore_image_defined_volumes = false
    max_concurrent_downloads = 3
    max_container_log_line_size = 16384
    netns_mounts_under_state_dir = false
    restrict_oom_score_adj = false
    sandbox_image = "registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.9"
    selinux_category_range = 1024
    stats_collect_period = 10
    stream_idle_timeout = "4h0m0s"
    stream_server_address = "127.0.0.1"
    stream_server_port = "0"
    systemd_cgroup = false
    tolerate_missing_hugetlb_controller = true
    unset_seccomp_profile = ""

    [plugins."io.containerd.grpc.v1.cri".cni]
      bin_dir = "/opt/cni/bin"
      conf_dir = "/etc/cni/net.d"
      conf_template = ""
      ip_pref = ""
      max_conf_num = 1

    [plugins."io.containerd.grpc.v1.cri".containerd]
      default_runtime_name = "runc"
      disable_snapshot_annotations = true
      discard_unpacked_layers = false
      ignore_rdt_not_enabled_errors = false
      no_pivot = false
      snapshotter = "overlayfs"

      [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime]
        base_runtime_spec = ""
        cni_conf_dir = ""
        cni_max_conf_num = 0
        container_annotations = []
        pod_annotations = []
        privileged_without_host_devices = false
        runtime_engine = ""
        runtime_path = ""
        runtime_root = ""
        runtime_type = ""

        [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime.options]

      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]

        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
          base_runtime_spec = ""
          cni_conf_dir = ""
          cni_max_conf_num = 0
          container_annotations = []
          pod_annotations = []
          privileged_without_host_devices = false
          runtime_engine = ""
          runtime_path = ""
          runtime_root = ""
          runtime_type = "io.containerd.runc.v2"

          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
            BinaryName = ""
            CriuImagePath = ""
            CriuPath = ""
            CriuWorkPath = ""
            IoGid = 0
            IoUid = 0
            NoNewKeyring = false
            NoPivotRoot = false
            Root = ""
            ShimCgroup = ""
            SystemdCgroup = true

      [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime]
        base_runtime_spec = ""
        cni_conf_dir = ""
        cni_max_conf_num = 0
        container_annotations = []
        pod_annotations = []
        privileged_without_host_devices = false
        runtime_engine = ""
        runtime_path = ""
        runtime_root = ""
        runtime_type = ""

        [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime.options]

    [plugins."io.containerd.grpc.v1.cri".image_decryption]
      key_model = "node"

    [plugins."io.containerd.grpc.v1.cri".registry]
      config_path = ""

      [plugins."io.containerd.grpc.v1.cri".registry.auths]

      [plugins."io.containerd.grpc.v1.cri".registry.configs]

      [plugins."io.containerd.grpc.v1.cri".registry.headers]

      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]

    [plugins."io.containerd.grpc.v1.cri".x509_key_pair_streaming]
      tls_cert_file = ""
      tls_key_file = ""

  [plugins."io.containerd.internal.v1.opt"]
    path = "/opt/containerd"

  [plugins."io.containerd.internal.v1.restart"]
    interval = "10s"

  [plugins."io.containerd.internal.v1.tracing"]
    sampling_ratio = 1.0
    service_name = "containerd"

  [plugins."io.containerd.metadata.v1.bolt"]
    content_sharing_policy = "shared"

  [plugins."io.containerd.monitor.v1.cgroups"]
    no_prometheus = false

  [plugins."io.containerd.runtime.v1.linux"]
    no_shim = false
    runtime = "runc"
    runtime_root = ""
    shim = "containerd-shim"
    shim_debug = false

  [plugins."io.containerd.runtime.v2.task"]
    platforms = ["linux/arm64/v8"]
    sched_core = false

  [plugins."io.containerd.service.v1.diff-service"]
    default = ["walking"]

  [plugins."io.containerd.service.v1.tasks-service"]
    rdt_config_file = ""

  [plugins."io.containerd.snapshotter.v1.aufs"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.btrfs"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.devmapper"]
    async_remove = false
    base_image_size = ""
    discard_blocks = false
    fs_options = ""
    fs_type = ""
    pool_name = ""
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.native"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.overlayfs"]
    mount_options = []
    root_path = ""
    sync_remove = false
    upperdir_label = false

  [plugins."io.containerd.snapshotter.v1.zfs"]
    root_path = ""

  [plugins."io.containerd.tracing.processor.v1.otlp"]
    endpoint = ""
    insecure = false
    protocol = ""

[proxy_plugins]

[stream_processors]

  [stream_processors."io.containerd.ocicrypt.decoder.v1.tar"]
    accepts = ["application/vnd.oci.image.layer.v1.tar+encrypted"]
    args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
    env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
    path = "ctd-decoder"
    returns = "application/vnd.oci.image.layer.v1.tar"

  [stream_processors."io.containerd.ocicrypt.decoder.v1.tar.gzip"]
    accepts = ["application/vnd.oci.image.layer.v1.tar+gzip+encrypted"]
    args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
    env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
    path = "ctd-decoder"
    returns = "application/vnd.oci.image.layer.v1.tar+gzip"

[timeouts]
  "io.containerd.timeout.bolt.open" = "0s"
  "io.containerd.timeout.shim.cleanup" = "5s"
  "io.containerd.timeout.shim.load" = "5s"
  "io.containerd.timeout.shim.shutdown" = "3s"
  "io.containerd.timeout.task.state" = "2s"

[ttrpc]
  address = ""
  gid = 0
  uid = 0

```
```
# 启动，并设置为开机启动 
sudo systemctl daemon-reload
sudo systemctl enable containerd
sudo systemctl start containerd 
# 查看是否启动成功 
sudo systemctl status containerd
```

# 4安装k8s
## 4.1修改系统文件
树莓派本身没启动croupmemory，需要在boot配置里修改成如下内容
```
sudo vi /boot/cmdline.txt
加入cgroup_enable=memory cgroup_memory=1
如（不能直接复制，因为每个机器的root=PARTUUID不一样）：
console=serial0,115200 console=tty1 root=PARTUUID=0b9ed906-02 rootfstype=ext4 fsck.repair=yes cgroup_enable=memory cgroup_memory=1 rootwait quiet splash plymouth.ignore-serial-consoles
```
保存后重启
## 4.2安装k8s
### 4.2.1换源和密钥
```sh-session
swapoff -a关闭分区！！！
sudo apt-get update && sudo apt-get install -y apt-transport-https安装依赖
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
### 4.2.2安装k8s
apt安装的kubelet kubectl 和kubeadm版本未必一致，一般安装k8s这三个组件一定要指定版本号，否则apt拉取最新版本可能会出现小版本错误，参考命令如下：
```
sudo apt-cache madison kubeadm 查看可用的版本
sudo apt install kubelet=1.28.2-00 kubectl=1.28.2-00 kubeadm=1.28.2-00
```
## 4.2.3.kubelet配置
为了实现containerd使⽤的cgroupdriver与kubelet使⽤的cgroup⼀致，修改kubelet配置。 配置成如下vim /etc/sysconfig/kubelet 
```
KUBELET_EXTRA_ARGS="--cgroup-driver=systemd" 
systemctl enable kubelet --now
```
## 4.3修改init启动配置文件
kubelet的cgroup管理员也要用systemd，debian或者ubuntu版本不像centos有kubelet的配置config文件，就得走初始化配置文件来配，所以kubeadm config print init-defaults > kubeadm-config.yaml
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
初始化后启用集群
```
mkdir -p $HOME/.kube  
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config  
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
### 5.1.1网络插件（cni）安装
主机安装完成后，从机自然会被主机安装（要有/etc/cni/net.d目录）
```
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.3/manifests/tigera-operator.yaml
curl -O -L https://raw.githubusercontent.com/projectcalico/calico/v3.26.3/manifests/custom-resources.yaml
```
修改custom-resources的子网号
```
kubectl create -f custom-resources.yaml
```
查看pod部署是否成功
```
watch kubectl get pods -n calico-system
```
如果失败了，如calico-kubeadm-controller一直是pending就查看containerd状态，可能是containerd异常导致calico没启动。这时重启一下containerd就ok
等到pod都running了
```
kubectl get node
```
显示Ready集群创建成功
## 5.2集群其他指令
### 5.2.1解散reset
reset后一定把containerd和kubelet重置
```
sudo kubeadm reset -f
sudo rm -rf /etc/kubernetes/ && sudo rm -rf /etc/cni && sudo rm -rf /var/lib/kubelet && sudo rm -rf /var/lib/etcd
sudo systemctl restart containerd
sudo systemctl restart kubelet
```
### 5.2.2查看细节描述
```
kubectl describe node +node名
kubectl describe pods -owide所有pod
kubectl describe pods 容器名 -n pod集群名
```

# 参考文献
1.[Containerd 安装 - 掘金 (juejin.cn)](https://juejin.cn/post/7053683649283096606)