"""例程微服务,综合了微服务的头、体、尾三个部分,并且可以通过继承的方式进行扩展"""
import os
import argparse
import time
from threading import Thread
from execution import Execution
from communication import Server, Client


class Microservice_main(Server, Execution, Client):
    """
    微服务主体
    """

    def __init__(
        self,
        serverIP=None,
        serverPort=None,
        clientIP=None,
        clientPort=None,
        microservice_name="Example",
    ):
        """
        初始化微服务的通讯模块，其中客户端IP表示该微服务作为客户端要连接的服务端IP,客户端Port表示该微服务作为客户端要连接的服务端Port。
        服务端IP表示该微服务作为服务端要监听的本机IP即端口，服务端Port表示该微服务作为服务端要监听的本机Port。
        """
        self.name = microservice_name
        self.__have_client = False
        self.__have_server = False
        if serverIP and serverPort:
            Server.__init__(self, serverIP, serverPort)
            self.__have_server = True
        if clientIP and clientPort:
            Client.__init__(self, clientIP, clientPort, clientName=clientIP + ":" + str(clientPort) + "_" + self.name)
            self.__have_client = True

        Execution.__init__(self)

        self.send_flag = False

    def microservice_run(self):
        """
        微服务运行函数，用于启动微服务
        """
        if self.__have_server:
            self.start_server()
        if self.__have_client:
            self.start_client()
        while True:
            time.sleep(0.1)

    def handle_data_received(self, data_received):
        """
        处理接收到的数据,这只是一个例程，需要自己实现
        所有处理数据要引用的外部函数或者类都在这里面进行修改
        """
        print("Infer result", data_received)

    def handle_request_client(self) -> None:
        """
        客户端连接服务器并发送指定的数据,这只是一个例程，需要自己实现
        """
        # 若微服务创建时不包含客户端，则无客户端处理函数，用于微服务尾
        if not self.__have_client:
            return
        # filepath = "./xxx.png"
        # self.send_file(filepath)
        while not self.send_flag:
            time.sleep(0.1)
        self.send_data(data="This is " + self.name)
        self.send_flag = False

    def handle_request_server(self, client_sock, client_name) -> None:
        """
        对套接字服务端接收到的数据进行处理,这只是一个例程，需要自己实现
        """
        # 若微服务创建时不包含服务器，则无服务器处理函数，用于微服务头
        if not self.__have_server:
            return
        # filename = self.receive_data(client_sock, fileaddr="./")
        # print(filename)
        received_data = self.receive_data(client_sock)
        self.handle_data_received(received_data)


def main():
    Microservice = Microservice_main(
        serverIP="127.0.0.1",
        serverPort=58589,
        microservice_name="cloud_start",
    )
    Microservice.microservice_run()

    # Microservice = Microservice_main(
    #     serverIP="localhost",
    #     serverPort=18000,
    #     microservice_name="Example_end",
    # )
    # Microservice.microservice_run()


if __name__ == "__main__":
    main()
