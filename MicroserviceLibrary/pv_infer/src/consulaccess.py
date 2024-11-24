import consul
import uuid


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

        # 打印服务的地址和端口
        # for svc in services:
        #     print(f"Address: {svc[0]}, Port: {svc[1]}")

        return services


# import consul
# import time


# class ConsulServiceRegistration:
#     def __init__(self, consul_address="localhost"):
#         self.consul_address = consul_address
#         self.consul_client = consul.Consul(host=consul_address)

#     def register_service(self, service_name, service_id, service_address, service_port, tags=None):
#         """
#         向 Consul 注册服务。
#         :param service_name: 服务名称
#         :param service_id: 服务 ID
#         :param service_address: 服务地址
#         :param service_port: 服务端口
#         :param tags: 服务标签（可选）
#         """
#         service_id = service_id or service_name
#         service_address = service_address or "localhost"

#         if tags:
#             tags = tags.split(",")

#         # 创建服务注册数据
#         service_register_data = {
#             "ID": service_id,
#             "Name": service_name,
#             "Address": service_address,
#             "Port": service_port,
#             "Tags": tags,
#             "Meta": {},
#             "Check": {
#                 "TTL": "5s",  # 服务检查间隔时间
#                 "HTTP": f"http://{service_address}:{service_port}/health",
#             },
#         }

#         # 注册服务
#         self.consul_client.agent.service.register(service_register_data)

#     def deregister_service(self, service_id):
#         """
#         从 Consul 取消注册服务。
#         :param service_id: 服务 ID
#         """
#         self.consul_client.agent.service.deregister(service_id)


# # 使用示例
# consul_address = "192.168.3.100"
# service_name = "my_service"
# service_id = "my_service_id"
# service_address = "192.168.3.33"
# service_port = 8080
# tags = "tag1,tag2"

# registration = ConsulServiceRegistration(consul_address)
# registration.register_service(service_name, service_id, service_address, service_port, tags)

# # 取消注册
# time.sleep(10)
# registration.deregister_service(service_id)
