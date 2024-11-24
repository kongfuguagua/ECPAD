# Consul

> 2024.5.29日更新  
> 本文对K8s部署consul进行简单介绍，并设置pv静态存储和nfs-nas动态存储配置。实现了k8s-consul与k8s自有注册数据库(etcd)同步。  
> 环境配置版本：==cri-containerd:v1.6.24== ====,====​==kubeadm kubeclt kubelet:v1.28.2==,==Helm:v3.15.1==  
> <font color="red">配置进行中可能会出现一些问题如，Not superuser、的权限问题，切换到root即可解决。文件权限问题使用 ls -ihl查看，chmod修改，k8s问题请查看日志和其他文档.</font>  
> 截至2024年5月29日helm的nfs源https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/可以使用

# 目录

###### 1K8S-etcd与consul

###### 2helm部署consul

###### 3consul的nfs持久化配置

###### 4K8S-consul使用

# 1K8S-etcd与consul

## 1.1K8S-etcd的crud(增删改查)

Kubernetes-etcd是一个高可用的键值存储系统，主要用于共享配置和服务发现，它通过Raft一致性算法处理日志复制以保证强一致性，我们可以理解它为一个高可用强一致性的服务发现存储仓库。  
在kubernetes集群中，etcd主要用于配置共享和服务发现  
Etcd主要解决的是分布式系统中数据一致性的问题，而分布式系统中的数据分为控制数据和应用数据，etcd处理的数据类型为控制数据，对于很少量的应用数据也可以进行处理。  
python的etcd3库可操作etcd数据库，下面给出crud示例

```
import etcd3
# 创建一个etcd3客户端
etcd = etcd3.client(
    host='192.168.3.38',
    port=2379,
    ca_cert='/etc/kubernetes/pki/etcd/ca.crt',
    cert_key='/etc/kubernetes/pki/etcd/server.key',
    cert_cert='/etc/kubernetes/pki/etcd/server.crt'
)
# 用于查询的key
key = '/registry/services/endpoints/default/mqttbroker001'
# 获取值和元数据
value, metadata = etcd.get(key)
print(value)
#key="try_2024_5_19"
#value="try_2024_5_19"
#etcd.put(key,value)#增加
#etcd.delete(key)#删除
#etcd.put(key,newvalue)#改
```

## 1.2consul

Consul 是一套开源的分布式服务发现和配置管理系统，由 HashiCorp 公司用 Go 语言开发。 提供了微服务系统中的服务治理、配置中心、控制总线等功能。这些功能中的每一个都可以根据需要单独使用，也可以一起使用以构建全方位的服务网格，总之Consul提供了一种完整的服务网格解决方案。它具有很多优点。包括： 基于 raft 协议，比较简洁； 支持健康检查, 同时支持 HTTP 和 DNS 协议 支持跨数据中心的 WAN 集群 提供图形界面 跨平台，支持 Linux、Mac、Windows

# 2helm部署consul

```
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install consul -n consul hashicorp/consul -f config.yaml
```

config.yaml文件内容

```
global:
  name: consul # 设置用于 Helm chart 中所有资源的前缀
ui:
  service: # 为 Consul UI 配置服务
    type: 'NodePort' # 服务类型为 NodePort
server:
  replicas: 1 # 要运行的服务器的数量，即集群数
  affinity: "" # 允许每个节点上运行更多的Pod
  storage: '2Gi' # 定义用于配置服务器的 StatefulSet 存储的磁盘大小
  storageClass: "" # 使用Kubernetes集群的默认 StorageClass
  securityContext: # 服务器 Pod 的安全上下文，以 root 用户运行
    fsGroup: 2000
    runAsGroup: 2000
    runAsNonRoot: false
    runAsUser: 0
syncCatalog:#与k8s同步
  enabled: true
```

等待pod变成running即可

```
kubectl get pod -n consul
```

注意此时如果没有配置持久化，consul-server会一直pending。配置pv或sc即可解决，下一章将详细介绍，持久化更详细介绍参考《K8S持久化的两种方法PV与SC》

# 3consul的nfs持久化配置

## 3.1PV静态持久化

静态PV和sc配置如下

```
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: consul
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-volume-consul-0
  labels:
    type: local
spec:
  capacity:
    storage: 2Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain  # 或者根据需要设置为 Recycle 或 Delete
  storageClassName: consul  # 只有当 PVC 需要引用这个存储类时才需要此字段，PV 本身不需要
  hostPath:
    path: "/consul/data"
```

## 3.2nfs动态持久化

配置好NAS-nfs以后，helm部署nfs。更详细介绍和配置参考《K8S持久化的两种方法PV与SC》

```
helm install nfs nfs-subdir-external-provisioner/nfs-subdir-external-provisioner -f config.yaml -n nfs
```

config.yaml参考

```
image:
  repository: registry.cn-hangzhou.aliyuncs.com/k-prometheus/nfs
  tag: v4.0.18
nfs:
  server: 192.168.3.64    #指定 NFS 服务器的地址
  path: /volume4/iiip          #指定 NFS 导出的共享数据目录
storageClass:
  defaultClass: true     #是否设置为默认的 StorageClass，本示例没设置，有需要的可以设置为 true
  name: nfs-sc            #指定 storageClass 的名字
```

# 4K8S-consul使用

consul的使用主要包括注册与查询两个模块，consul也支持保存服务配置，不过这项功能和K8S冲突，因此我们只使用consul用作服务注册与查询

consul支持http查询，例如通过`curl`​命令，通过GET或者PUT等方法即可进行操作，我们假设已经有一个consul服务器地址：192.168.3.100:8500

## 1. 直接命令查询

```bash
# 查询所有服务列表
curl http://192.168.3.100:8500/v1/catalog/services
# 查询某个服务的详细配置，例如IP
curl http://192.168.3.200:31995/v1/catalog/service/iiip-redis-core
```

第一条命令的返回如下

```bash
HTTP/1.1 200 OK
Content-Length: 744
Connection: keep-alive
Content-Type: application/json
Date: Thu, 30 May 2024 15:06:03 GMT
keep-alive: timeout=4
Proxy-Connection: keep-alive
Vary: Accept-Encoding
X-Consul-Default-Acl-Policy: allow
X-Consul-Effective-Consistency: leader
X-Consul-Index: 47218
X-Consul-Knownleader: true
X-Consul-Lastcontact: 0
X-Consul-Query-Backend: blocking-query

{
  "alertmanager-main-monitoring": [
    "k8s"
  ],
  "alertmanager-operated-monitoring": [
    "k8s"
  ],
  "blackbox-exporter-monitoring": [
    "k8s"
  ],
  "calico-api-calico-apiserver": [
    "k8s"
  ],
  "calico-kube-controllers-metrics-calico-system": [
    "k8s"
  ],
  "calico-typha-calico-system": [
    "k8s"
  ],
  "consul": [],
  "consul-connect-injector-consul": [
    "k8s"
  ],
  "consul-dns-consul": [
    "k8s"
  ],
  "consul-server-consul": [
    "k8s"
  ],
  "consul-ui-consul": [
    "k8s"
  ],
  "grafana-monitoring": [
    "k8s"
  ],
  "iiip-mqttbroker001-utils": [
    "k8s"
  ],
  "iiip-redis-core": [
    "k8s"
  ],
  "kube-state-metrics-monitoring": [
    "k8s"
  ],
  "kubernetes-default": [
    "k8s"
  ],
  "node-exporter-monitoring": [
    "k8s"
  ],
  "prometheus-adapter-monitoring": [
    "k8s"
  ],
  "prometheus-k8s-monitoring": [
    "k8s"
  ],
  "prometheus-operated-monitoring": [
    "k8s"
  ],
  "prometheus-operator-monitoring": [
    "k8s"
  ]
}

```

第二条命令的返回如下

```bash
HTTP/1.1 200 OK
Content-Length: 638
Connection: keep-alive
Content-Type: application/json
Date: Thu, 30 May 2024 15:03:43 GMT
keep-alive: timeout=4
Proxy-Connection: keep-alive
Vary: Accept-Encoding
X-Consul-Default-Acl-Policy: allow
X-Consul-Effective-Consistency: leader
X-Consul-Index: 44663
X-Consul-Knownleader: true
X-Consul-Lastcontact: 0
X-Consul-Query-Backend: blocking-query

[
  {
    "ID": "",
    "Node": "k8s-sync",
    "Address": "127.0.0.1",
    "Datacenter": "dc1",
    "TaggedAddresses": null,
    "NodeMeta": {
      "external-source": "kubernetes"
    },
    "ServiceKind": "",
    "ServiceID": "iiip-redis-core-b6d8976ede75",
    "ServiceName": "iiip-redis-core",
    "ServiceTags": [
      "k8s"
    ],
    "ServiceAddress": "192.168.3.200",
    "ServiceWeights": {
      "Passing": 1,
      "Warning": 1
    },
    "ServiceMeta": {
      "external-k8s-ns": "core",
      "external-source": "kubernetes",
      "port-redisport": "6379"
    },
    "ServicePort": 32211,
    "ServiceSocketPath": "",
    "ServiceEnableTagOverride": false,
    "ServiceProxy": {
      "Mode": "",
      "MeshGateway": {},
      "Expose": {}
    },
    "ServiceConnect": {},
    "ServiceLocality": null,
    "CreateIndex": 44663,
    "ModifyIndex": 44663
  }
]
```

注册服务也可以通过http的PUT或POST命令直接进行，但是不太方便，下面将基于两种语言介绍具体细节

## 2.Go

### 注册

通过`"github.com/hashicorp/consul/api"`​进行使用，注册时的基本信息为服务名字、服务ID、服务地址、服务端口、健康检查地址

```go
err = consulClient.Agent().ServiceRegister(&api.AgentServiceRegistration{
	Name:    service_name,
	ID:      service_id,
	Address: service_address,
	Port:    service_port,
	Check: &api.AgentServiceCheck{
		HTTP:     health_address,
		Interval: "10s",
		Timeout:  "1s",
	},
})
```

在服务关闭的时候，需要取消注册

```go
deregErr := consulClient.Agent().ServiceDeregister("my-service-id")
```

### 查询

下述示例代码展示了一个根据服务名称从consul中查询服务ip的实现

```go
func getIpPortFromConsul(servicename string) string {
	// 创建 Consul 客户端配置
	config := api.DefaultConfig()
	config.Address = "192.168.3.200:31995" // 替换为你的 Consul 地址和端口

	// 创建 Consul 客户端
	client, err := api.NewClient(config)
	if err != nil {
		panic(err)
	}

	// 查询服务的健康实例
	services, _, err := client.Health().Service(servicename, "", true, nil)
	if err != nil {
		panic(err)
	}

	// 提取服务的地址和端口
	var ipstring string
	for _, service := range services {
		ipstring = service.Service.Address + ":" + fmt.Sprintf("%d", service.Service.Port)
		break
	}
	return ipstring
}
```

关于consul服务注册的使用，可以参阅示例代码，示例代码向consul服务器注册了一个示例服务，并在8080端口提供了一个helloworld响应服务，以及相应的健康检查。requestservice会向consul查询这个服务的ip地址并向其发送服务请求。代码地址为：[SJTU-IIIP/StudyExample/consultest at master · MaxsunCai/SJTU-IIIP (github.com)](https://github.com/MaxsunCai/SJTU-IIIP/tree/master/StudyExample/consultest)

使用方式为：

1. 进入testservice文件夹，`go run . --consulip=192.168.3.100:8500(你的consul地址)`​
2. 进入requestservice文件夹，`go run . --consulip=192.168.3.100:8500(你的consul地址)`​

## 3.Python

和go的方法大同小异，使用python-consul库，`import consul`​，下面是一个简单的注册和查询服务IP的实现

```python
class ConsulAccess(object):
    def __init__(self, host: str = "127.0.0.1", port: int = 8500) -> None:
        self.consul_client = consul.Consul(host=host, port=port)

    def register_service(self, service_name: str, service_ip: str, service_port: int) -> None:

        service = {
            "ID": str(uuid.uuid4()),  # 唯一标识服务的 ID
            "Name": service_name,  # 服务的名称
            "Tags": ["source"],  # 服务的标签列表
            "Address": service_ip,  # 服务的地址
            "Port": service_port,  # 服务的端口
            "Check": {
                "HTTP": "http://" + service_ip + ":" + str(service_port) + "/health",  # 健康检查的 HTTP 端点
                "Interval": "10s",  # 健康检查间隔
            },
        }
        # 注册服务
        self.consul_client.agent.service.register(service)

    def serach_service(self, service_name: str) -> list:
        # 连接到 Consul 实例
        service_list = self.consul_client.health.service(service_name, passing=True)

        # 提取服务的地址和端口
        services = []
        for svc in service_list[1]:
            service = svc["Service"]
            address = service["Address"]
            port = service["Port"]
            services.append((address, port))

        return services
```

总体而言，consul的使用比较简单，可以借助AI直接查询使用方法，后续开发步入正轨后会给出相应的标准接入库

‍
