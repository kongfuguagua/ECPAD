## 目录
###### 一、安装操作系统
###### 二、检查已安装组件
###### 三、安装pytorch
###### 四、安装jtop
###### 五、docker配置及使用




## 一、安装操作系统

参考官网教程[Get Started With Jetson Nano Developer Kit | NVIDIA Developer](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit#intro)
##### 1.下载官方镜像，目前最新版本是jetpack 4.6.1
##### 2.格式化SD卡并烧录镜像
##### 3.烧写完成后，将SD卡插入Jetson Nano,开机
##### 4.完成初次启动的设置
##### ==5.安装网卡驱动==
参考 https://resource.tp-link.com.cn/pc/docCenter/showDoc?id=1700032206086984
下载Linux驱动程序，用U盘拷贝到Jetson Nano
运行命令，确认系统架构为arm64
```sh-session
dpkg --print-architecture
```
使用aic8800fdrvpackage_arm64.deb，安装命令：
```sh-session
sudo dpkg -i aic8800fdrvpackage_arm64.deb
```
完成后可以连接WIFI，通过ssh进行后续操作

## 二、检查已安装组件
参考博客 [玩转Jetson Nano（二）检查已安装组件_jetsonnano安装组件-CSDN博客](https://blog.csdn.net/beckhans/article/details/89138876?spm=1001.2014.3001.5501)
##### 0.关于更新源
==根据参考博客中所说，不建议更换源。尝试了国内几大源，都会出现一些报错，因此不考虑换源==
更新
```sh-session
sudo apt-get update
sudo apt-get upgrade
```
**这可能需要花较长的时间**
##### 1.检查CUDA
在官方镜像中是包含CUDA 10.2的，但是需要你把CUDA的路径写入环境变量中。使用自带Vim工具运行下面的命令编辑环境变量
```sh-session
sudo vi ~/.bashrc
```
在文件最后添加下面内容：
```vim
export CUDA_HOME=/usr/local/cuda-10.2
export LD_LIBRARY_PATH=/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH
export PATH=/usr/local/cuda-10.2/bin:$PATH
```
最后运行
```sh-session
source ~/.bashrc
```
此时可以执行nvcc -V查看CUDA版本
##### 2.检查cuDNN
Jetson-nano中已经安装好了cuDNN，并有例子可供运行
```sh-session
cd /usr/src/cudnn_samples_v7/mnistCUDNN   #进入例子目录
sudo make     #编译一下例子
sudo chmod a+x mnistCUDNN  #为可执行文件添加执行权限
./mnistCUDNN  #执行
```
初次运行会有报错，需要安装libfreeimage3
```sh-session
sudo apt-get install libfreeimage3 libfreeimage-dev
```
再次在/usr/src/cudnn_samples_v7/mnistCUDNN目录下执行./mnistCUDNN可以正常运行

## 三、安装pytorch
安装pip
```sh-session
sudo apt-get install python3-pip python3-dev
python3 -m pip install --upgrade pip  #升级pip
```
升级完后使用pip会有warning：
```sh-session
WARNING: pip is being invoked by an old script wrapper. This will fail in a future version of pip.
Please see https://github.com/pypa/pip/issues/5599 for advice on fixing the underlying issue.
To avoid this problem you can invoke Python with '-m pip' instead of running pip directly.
```
解决有些麻烦，可以选择忽略，或者在pip前面加上"python3 -m"
jetson的pytorch安装有些不同，到官网查找合适的pytorch版本[PyTorch for Jetson - Jetson & Embedded Systems / Announcements - NVIDIA Developer Forums](https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048)
jetpack版本为4.6.1，可以安装PyTorch v1.10.0
![[Pasted image 20240711111810.png]]
下载对应文件并拷贝到jetson nano中
运行下列命令
```sh-session
sudo pip3 install torch-1.10.0-cp36-cp36m-linux_aarch64.whl
```
安装完成并验证
新建test.py文件
```python
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
运行
```sh-session
python3 test.py
```
结果如下，可以正常使用
![[Pasted image 20240711112437.png]]
## 四、安装jtop
参考[jetson-stats · PyPI](https://pypi.org/project/jetson-stats/)
使用pip安装jetson-stats
```
sudo -H pip3 install -U jetson-stats
```
运行jtop
```
jtop
```
出现报错
```
I can't access jtop.service.
Please logout or reboot this board.
```
需要重启，重启后运行jtop效果如下
![[Pasted image 20240711184524.png]]
可以正常使用，但有以下问题
![[Pasted image 20240711211634.png]]
在github上发现很多人有同样问题
==jetpack4.6.5是2024.06.28发布的，截至7.12 jetson-stats开发者还未发布新版本==
<font color="red">更新</font>
发现解决方案，修改配置文件
```
cd /usr/local/lib/python3.6/dist-packages/jtop
```
再进行如下修改
修改__init__.py和core/jetson_variables.py
![[Pasted image 20240712183953.png]]
再重启jetson_stats
```
sudo systemctl restart jtop.service
```
再运行jtop，不会再出现上面问题。
## 五、docker配置及使用
##### 1.docker配置
参考nvidia配置k8s-cridocker开发文档
在/etc/docker/daemon.json中添加语句

```sh-session
{
"registry-mirrors": ["https://svph38nh.mirror.aliyuncs.com"],
"exec-opts": ["native.cgroupdriver=systemd"]
}
```
重启docker

```sh-session
sudo systemctl daemon-reload
sudo systemctl restart docker
```
实际使用时没有进行配置也能正常使用
##### 2.拉取镜像
在官网查看需要的镜像 [https://ngc.nvidia.com/catalog/containers](https://ngc.nvidia.com/catalog/containers)
本次选择的镜像为NVIDIA L4T PyTorch在[NVIDIA L4T PyTorch | NVIDIA NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-pytorch)
找到对应版本可以看到以下信息：
- JetPack 4.6.1 (L4T R32.7.1)
    
    - l4t-pytorch:r32.7.1-pth1.9-py3
        - PyTorch v1.9.0
        - torchvision v0.10.0
        - torchaudio v0.9.0
    - l4t-pytorch:r32.7.1-pth1.10-py3
        - PyTorch v1.10.0
        - torchvision v0.11.0
        - torchaudio v0.10.0

选择l4t-pytorch:r32.7.1-pth1.10-py3，拉取镜像

```
sudo docker pull nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3
```
启动镜像，并保证能调用主机GPU
```
sudo docker run -it --rm --runtime nvidia --network host nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3
```
在镜像中运行nvcc -V并进行test.py的验证，表示可以调用GPU