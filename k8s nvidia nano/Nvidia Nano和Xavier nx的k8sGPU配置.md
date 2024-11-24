==写在前面==
<font color="red">nano和Xavier nx的内核、GPU驱动、CUDA版本都不一样这里仅仅介绍安装和测试docker镜像，具体能否实现训练功能未知！请自行测试！！！</font>

>2024.7.17日更新
本文对NVIDIA系列Nano和Xavier nx进行k8s-GPU插件部署和前序操作。
环境配置版本：==cri-docker=0.3.11 ==,==kubeadm kubeclt kubelet=v1.28.2==，==Nano cuda10.2==,==Xavier nx cuda11.4==
本文不涉及nvdia操作系统和gpu、cuda安装，默认设备正常，裸机正常使用cuda
><font color="red">配置进行中可能会出现一些如，Not superuser、的权限问题，切换到root即可解决。文件权限问题使用 ls -ihl查看，chmod修改.</font>
>截至2024.7.17日k8s阿里源可以使用
# 目录
###### 1安装nvidia-docker2
###### 2修改docker及其配置
###### 3k8s安装nvidia-device-plugin
###### 4验证运行GPU(镜像版本)
###### 5镜像dubug
# 1安装nvidia-docker2
Xavier nx默认安装，可skip

设置NVIDIA Container Toolkit的stable版本存储库的GPG key：
```
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```
更新源并安装nvidia-container-toolkit
```
sudo apt-get update 
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```
这一步后docker应该可以使用GPU，测试
```
docker run -it --rm --runtime nvidia --network host nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3
```
如果出现报错请检查/etc/docker/daemon.json是否设置nvidia runtime，即
```
{
"runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
```
# 2修改docker及其配置
k8s如果想使用GPU，需要设置nvidia的运行时作为默认runtime，即参考官网[Installing the NVIDIA Container Toolkit — NVIDIA Container Toolkit 1.15.0 documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)。
如果是k8s基于docker则：
```
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```
即/etc/docker/daemon.json全部配置为：
```
{
    "default-runtime": "nvidia",
    "exec-opts": [
        "native.cgroupdriver=systemd"
    ],
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
```
# 3k8s安装nvidia-device-plugin
直接部署即可
```
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.12.3/nvidia-device-plugin.ymlkubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.12.3/nvidia-device-plugin.yml
```
如果网络顺畅等待Running
查看logs显示，如下监测到nvidia/GPU即为成功。
注意nano为Detected Tegra platform: /etc/nv_tegra_release found
Xavier nx为 Detected Tegra platform: /sys/devices/soc0/family has 'tegra' prefix
![[Pasted image 20240717135715.png]]
# 4验证运行GPU(镜像版本)
测试文件如下
```
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  restartPolicy: Never
  nodeSelector:
    kubernetes.io/hostname: nvidia001 # 指定调度到节点名为nvidia001的节点
  containers:
    - name: cuda-container
      image: nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3
      command: ["sleep"]
      args: ["infinity"]
      resources:
        limits:
          nvidia.com/gpu: 1  # 请求1个GPU
  tolerations:
    - key: nvidia.com/gpu
      operator: Exists
      effect: NoSchedule
```
注意完成上述k8s已经可以检测到GPU，下面如果出现什么问题请检测镜像是否正常！
执行测试python测试文件：
```
import torch
# 打印CUDA是否可用
print("Is CUDA available: ", torch.cuda.is_available())
# 尝试创建一个在GPU上的张量
if torch.cuda.is_available():
    print("CUDA version: ", torch.version.cuda)
    print("Number of GPUs: ", torch.cuda.device_count())
    print("Names of GPUs: ", torch.cuda.get_device_name(0))  # 列出第一个GPU的名字
    x = torch.tensor([1.0, 2.0], dtype=torch.float32).cuda()  # 将张量移动到GPU
    print("Tensor on GPU: ", x)
else:
    print("CUDA is not available. Please check your setup.")
```
# 5镜像dubug
使用r32版本的镜像，如nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3会出现：
![[Pasted image 20240717140450.png]]
这是镜像本身问题，确定镜像cuda版本后，可以在镜像/usr/local/cuda-10.2/targets/aarch64-linux/lib/目录下重新拷贝文件修改镜像,软链接问题再/usr/lib复制。具体文件见附件。
以cuda10.2版本为例
删除镜像内/usr/local/cuda-10.2/targets/aarch64-linux/lib/下所有文件
将正常的/usr/local/cuda-10.2/targets/aarch64-linux/lib/下文件导入，可用命令
```
docker cp /usr/local/cuda-10.2/targets/aarch64-linux/lib/ 容器名:/usr/local/cuda-10.2/targets/aarch64-linux/lib/
```
导入后运行，发现报错改为：
![[Pasted image 20240717152602.png]]
原因为修改上述库后，应修改链接库，粘贴正常的/usr/lib/aarch64-linux-gnu/libcudnn.so.8后报错又变为：
![[Pasted image 20240717152809.png]]
原因是libcudnn.so.8为软连接，执行
```
ls -l /usr/lib/aarch64-linux-gnu/libcudnn.so.8
```
将输出文件再加入即可完成。