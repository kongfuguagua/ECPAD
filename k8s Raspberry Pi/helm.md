==写在前面==
<font color="red">每个jccount账号只能登录10个设备.</font>
<font color="red">出现bug需要重启时，先重启containerd后重启kubelet.</font>

>2023.10.11日更新
本文对树莓派4B进行helm安装
环境配置版本：==cri-containerd:v1.6.24 ==,==kubeadm kubeclt kubelet:v1.28.2==,==Helm:v3.15.1==
><font color="red">配置进行中可能会出现一些如，Not superuser、的权限问题，切换到root即可解决。文件权限问题使用 ls -ihl查看，chmod修改.</font>

# 目录
###### 1helm介绍
###### 2helm安装
###### 3helm使用
###### 4参考文档

# 1helm介绍
`Helm` 是 Kubernetes 的包管理器。包管理器类似于我们在 Ubuntu 中使用的apt、Centos中使用的yum 或者Python中的 pip 一样，能快速查找、下载和安装软件包。Helm 由客户端组件 helm 和服务端组件 Tiller 组成, 能够将一组K8S资源打包统一管理, 是查找、共享和使用为Kubernetes构建的软件的最佳方式。
Helm 包含两个组件，分别是 helm 客户端 和 Tiller 服务器：
- `helm` 是一个命令行工具，用于本地开发及管理chart，chart仓库管理等
- `Tiller` 是 Helm 的服务端。Tiller 负责接收 Helm 的请求，与 k8s 的 apiserver 交互，根据chart 来生成一个 release 并管理 release
- `chart Helm`的打包格式叫做chart，所谓chart就是一系列文件, 它描述了一组相关的 k8s 集群资源
- `release` 使用 helm install 命令在 Kubernetes 集群中部署的 Chart 称为 Release
- `Repoistory Helm chart` 的仓库，Helm 客户端通过 HTTP 协议来访问存储库中 chart 的索引文件和压缩包
chart的目录树
```
wordpress/
  Chart.yaml          # 用于描述 chart 信息的 yaml 文件
  LICENSE             # 可选：用于存储关于 chart 的 LICENSE 文件
  README.md           # 可选：README 文件
  values.yaml         # 用于存储 chart 所需要的默认配置
  values.schema.json  # 可选: 一个使用JSON结构的 values.yaml 文件
  charts/             # 包含 chart 所依赖的其他 chart
  crds/               # 自定义资源的定义
  templates/          # chart 模板文件，引入变量值后可以生成用于 Kubernetes 的 manifest 文件
  templates/NOTES.txt # 可选: 包含简短使用说明的纯文本文件
```
# 2helm安装
用二进制版本安装
每个Helm [版本](https://github.com/helm/helm/releases)都提供了各种操作系统的二进制版本，这些版本可以手动下载和安装。
1. 下载 [需要的版本](https://github.com/helm/helm/releases)
2. 解压(`tar -zxvf helm-v3.0.0-linux-amd64.tar.gz`)
3. 在解压目录中找到`helm`程序，移动到需要的目录中(`mv linux-amd64/helm /usr/local/bin/helm`)
然后就可以执行客户端程序并 [添加稳定仓库](https://helm.sh/zh/docs/intro/quickstart/#%e5%88%9d%e5%a7%8b%e5%8c%96): `helm help`
# 3helm使用
下面列出了常用的helm指令，更多指令参考官方文档
```
添加仓库
helm repo add stable https://charts.helm.sh/stable
仓库更新
helm repo update
搜索安装包，如consul
helm search repo consul
安装consul
helm install consul stable/consul
查看已部署的的chart
helm list
卸载chart
helm uninstall
```
# 4参考文档
[Helm | 使用Helm](https://helm.sh/zh/docs/intro/using_helm/)
[Helm从入门到实践-腾讯云开发者社区-腾讯云 (tencent.com)](https://cloud.tencent.com/developer/article/2170804)
[Helm入门（一篇就够了）-阿里云开发者社区 (aliyun.com)](https://developer.aliyun.com/article/1207395)