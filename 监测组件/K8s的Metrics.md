==写在前面==
kubectl top，这个命令需要有对应的metrics接口，如果不安装metrics-server，使用top命令查看Pod的CPU、内存使用过程中，会遇到以下问题：error: Metrics API not available
安装metric-server组件可以参考Github上的安装参考资料： https://github.com/kubernetes-sigs/metrics-server
### 下载部署文件
```
wget https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml -O metrics-server-components.yaml
```
需要注意的是，metrics-server镜像用的是gcr镜像，需要换到国内的镜像仓库
```
sed -i 's/registry.k8s.io\/metrics-server/registry.cn-hangzhou.aliyuncs.com\/google_containers/g' metrics-server-components.yaml
```

### 修改tls校验
```
      containers:
      - args:
        ...
        - --kubelet-insecure-tls

```
apply即可


参考# k8s集群安装metrics-server解决error: Metrics API not available问题