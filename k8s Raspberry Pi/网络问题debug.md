# calico-node报错Readiness probe failed: calico/node is not ready: BIRD is not ready处理办法
# 1查看节点问题
kubectl get pod --alll-namespaces
kubectl describe pod calico-node-q7k7p -n calico-system
# 2查看ip
发现是使用了其他网桥的ip
calicoctl get node containerdmaster -o yaml
# 3修改
```
calicoctl patch node containerdmaster --patch='{"spec":{"bgp": {"ipv4Address": "10.180.224.46/15"}}}' --allow-version-mismatch
calicoctl patch node containerdmaster --patch='{"spec":{"addresses": {"address":"10.180.224.46/15"}}}' --allow-version-mismatch
calicoctl get node containerdmaster -o yaml --allow-version-mismatch > calico_master.yaml
calicoctl apply -f calico_master.yaml --allow-version-mismatch
```
完成！
# 附录安装calicoctl
# ！calicoctl与calico版本一致
查看calico版本
```
kubectl describe pod calico-node-q7k7p -n calico-system
查看镜像版本即可
```
安装
```
curl -L https://github.com/projectcalico/calico/releases/download/v3.27.0/calicoctl-linux-arm64 -o calicoctl
chmod +x calicoctl
```
如果无法执行calicoctl。将文件转移到usr/local/bin文件即可