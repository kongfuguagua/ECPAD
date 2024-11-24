==写在前面==
由于docker desktop基于WSL的虚拟化，其docker不能启动windows系统的端口监听。即可以ping通，不能telnet端口
解决方案，采用dind（docker in docker）技术，docker中运行一个容器并开放swarm监听端口，容器内的docker可以驱动端口监听。

友情链接： [[树莓派k8s-cridockerd]]
# swarm集群初始化及配置
## 1.1 dind镜像拉取
1先进入wsl路径，输入wsl。因为swarm操作建议进入wsl系统中进行，因为在虚拟化系统中配了简单命令：did = docker swarm exec，否则在cmd里执行会较麻烦。
==注意！！！后续所有docker操作如dockers node ls、docker ps -a 都要前面加did，因为是在dind容器部署的swarm。==
2 vim /etc/profile 中输入alias did="docker exec swarm"配置did命令
3 pull dind镜像，docker pull docker:dind
4在swarm没初始化下运行镜像，docker run -dit --privileged --name swarm -p 2377:2377 docker:dind
## 1.2 集群初始化
did docker swarm init --advertise-addr ==暴露的ip地址,如192.168.0.3==
运行成功后会显示工作节点加入token复制下后去从机运行即可。

# 常用指令
netstat -na | findstr 2377查看2377端口开放情况
netstat -nao查看全部端口
docker swarm leave工作节点离开集群
dockerswarm leave -force管理节点离开集群