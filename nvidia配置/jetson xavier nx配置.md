==基本与jetson nano配置文件内容相同==
<font color="red">下面介绍不同点</font>
## 一、安装操作系统
参考[Jetson 系列——nvidia jetson xavier nx重新烧录系统_jetson xavier nx 烧录-CSDN博客](https://blog.csdn.net/weixin_42264234/article/details/118651370)
官方网站已经找不到SD卡镜像了，从以下网站下载镜像
https://developer.nvidia.com/jetson-nx-developer-kit-sd-card-image
对应jetpack版本5.0.2
==网卡驱动不需要装，自带WiFi==
## 二、检查已安装组件
CUDA版本不同，添加内容不同：
```vim
export CUDA_HOME=/usr/local/cuda-11.4
export LD_LIBRARY_PATH=/usr/local/cuda-11.4/lib64:$LD_LIBRARY_PATH
export PATH=/usr/local/cuda-11.4/bin:$PATH
```
cuDNN版本也不同，需要验证时请自行改正。
## 三、安装pytorch

到官网查找合适的pytorch版本[PyTorch for Jetson - Jetson & Embedded Systems / Announcements - NVIDIA Developer Forums](https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048)
jetpack版本为5.0.2，可以安装PyTorch v1.13.0
![[Pasted image 20240713205933.png]]
下载对应文件并拷贝到xavier nx中
运行下列命令
```sh-session
sudo pip3 install torch-1.13.0a0+d0d6b1f2.nv22.10-cp38-cp38-linux_aarch64.whl
```
验证过程中可能遇到问题ImportError: libopenblas.so.0: cannot open shared object file: No such file or directory
下载
```
sudo apt-get install libopenblas-dev
```
其余内容不变
## 四、安装jtop
当前版本支持jetpack5.0.2，不需要修改
## 五、docker拉取镜像
在官网查看需要的镜像 [https://ngc.nvidia.com/catalog/containers](https://ngc.nvidia.com/catalog/containers)
本次选择的镜像为NVIDIA L4T PyTorch在[NVIDIA L4T PyTorch | NVIDIA NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-pytorch)
找到对应版本可以看到以下信息：
![[Pasted image 20240713210432.png]]
选择l4t-pytorch:r35.1.0-pth1.13-py3，拉取镜像

```
sudo docker pull nvcr.io/nvidia/l4t-pytorch:r35.1.0-pth1.13-py3
```
启动镜像，并保证能调用主机GPU
```
sudo docker run -it --rm --runtime nvidia --network host nvcr.io/nvidia/l4t-pytorch:r35.1.0-pth1.13-py3
```
在镜像中运行nvcc -V并进行test.py的验证，表示可以调用GPU