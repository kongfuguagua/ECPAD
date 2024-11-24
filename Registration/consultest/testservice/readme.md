go语言示例微服务框架

main.go

创建http服务器，连接consul注册微服务

execution.go

服务逻辑部分

### 示例运行

go run . --consulip=192.168.3.100:8500

### 示例请求格式，其中IP和Port需要替换为服务所在机器的IP和端口

示例请求: curl -X POST http://IP:Port/service -d "hello, world"