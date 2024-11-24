"""例程微服务,综合了微服务的头、体、尾三个部分,并且可以通过继承的方式进行扩展"""
import os
import argparse
import time
import threading
from threading import Thread
from communication import Server, Client
from execution import Execution


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
        # 微服务名字,用于区分不同的微服务
        self.name = microservice_name

        # 用于判断是否有客户端和服务端
        self.__have_client = False
        self.__have_server = False

        # 初始化通讯模块
        if serverIP and serverPort:
            Server.__init__(self, serverIP, serverPort)
            self.__have_server = True
        if clientIP and clientPort:
            # 客户端名字目前是IP+端口+微服务名字，后续需要确定为微服务架构下的统一命名规则
            Client.__init__(self, clientIP, clientPort, clientName=clientIP + ":" + str(clientPort) + "_" + self.name)
            self.__have_client = True

        # 初始化数据处理模块
        Execution.__init__(self)

        # 用于存储处理后的数据
        self.executed_data = None
        # 该微服务是否涉及到对多个客户端的数据联合处理，若涉及到，需要将其打开
        self.multi_client_data_process = False

    def multi_client_data_process_init(self):
        """
        初始化多客户端数据联合处理模块，这里面是需要共同操作的数据
        """
        self.multi_data = {}
        self.lock = threading.Lock()

        thread = Thread(target=self.handle_data_from_multi_client)
        # 设置成守护线程
        thread.setDaemon(True)
        thread.start()

    def handle_data_from_multi_client(self):
        # 同时处理多个客户端的数据，例程，需要自己实现
        while True:
            # 所有线程的数据来自于self.multi_data数据库，确保收到所有数据后进入程序进行处理
            while True:
                # 用于确实接收到的数据是否达到了要求，若没有达到要求则继续等待
                continue_flag = False
                for value in self.multi_data.values():
                    if value is None:
                        continue_flag = True
                        break
                if continue_flag:
                    time.sleep(0.1)
                    continue
                else:
                    break
            data = self.multi_data
            self.multi_run(data)
            # 程序处理完数据后，将数据清空，以便下一次接收数据
            self.lock.acquire()
            for key in self.multi_data.keys():
                self.multi_data[key] = None
            self.lock.release()
            # 程序结束之后，重新进入循环等待下一个全局数据处理

    def microservice_run(self):
        """
        微服务运行函数，用于启动微服务
        """
        # 若需要启用多客户端数据联合处理功能，将self.multi_client_data_process设置为True再启动即可
        if self.multi_client_data_process:
            self.multi_client_data_process_init()

        # 先启动客户端再启动服务端,因为服务端启动后会监听端口产生阻塞,后续会将端口监听尝试独立成一个线程,不产生阻塞TODO:
        # 后续需要增加客户端和服务端的断线重连等功能TODO:
        if self.__have_client:
            self.start_client()
        if self.__have_server:
            # 服务器启动后程序会一直在这里面阻塞不断监听新的客户端连接,后面的while true实际上并不会进入
            self.start_server()
        while True:
            time.sleep(0.1)

    def handle_data_received(self, data_received, client_name=None):
        """
        处理接收到的数据,这只是一个例程，需要自己实现
        所有处理数据要引用的外部函数或者类都在这里面进行修改
        """
        # 调用Execution中的函数进行数据处理
        self.executed_data = self.run(data_received, client_name)

    def handle_request_client(self) -> None:
        """
        客户端连接服务器并发送指定的数据,这只是一个例程，需要自己实现
        """
        # 若微服务创建时不包含客户端，则无客户端处理函数，用于微服务尾
        if not self.__have_client:
            return

        # 文件传输的支持
        # filepath = "./xxx.png"
        # self.send_file(filepath)

        # 一般数据的发送,若data的数据类型不是str，那么需要自己实现encode函数，encode函数即为将自己的数据类型转换为bytes
        while True:
            self.send_data(data="This is " + self.name)
            time.sleep(1)

    def handle_request_server(self, client_sock, client_name) -> None:
        """
        对套接字服务端接收到的数据进行处理,这只是一个例程，需要自己实现
        """
        # 若微服务创建时不包含服务器，则无服务器处理函数，用于微服务头
        if not self.__have_server:
            return
        # 文件传输的支持
        # filename = self.receive_data(client_sock, fileaddr="./")
        # print(filename)

        # 一般数据的传输,接收到后可直接传给数据处理模块
        received_data = self.receive_data(client_sock)

        # 利用线程锁，实现对全局数据库的数据存储
        # 注意，此时接受到的数据是没有时刻的先后关系的，如果要出现时刻的不同需要对字典进行简单的修改
        if self.multi_client_data_process:
            self.lock.acquire()
            self.multi_data[client_name] = received_data
            self.lock.release()

        # 自带的数据处理
        self.handle_data_received(received_data, client_name=client_name)

    """
    # 用于对数据进行编码和解码,默认支持字符串和文件，如果需要其他类型的数据传输，需要自己实现
    def encode(self, data) -> str:
        return data

    def decode(self, data: str):
        return data
    """


def main():
    #####使用方式1,和k8s结合使用,使用环境变量传入参数#####
    defaultReceiveIP = os.environ.get("MY_POD_IP")
    defaultServerPort = os.environ.get("INFERENCE_SERVICE_PORT_INPUTSERVER")
    defaultOutputIP = os.environ.get("OUTPUT_SERVICE_HOST")
    defaultClientPort = os.environ.get("OUTPUT_SERVICE_PORT_OUTPUTSERVER")
    parser = argparse.ArgumentParser()
    parser.add_argument("--serverip", type=str, default=defaultReceiveIP)
    parser.add_argument("--serverport", type=int, default=defaultServerPort)
    parser.add_argument("--clientip", type=str, default=defaultOutputIP)
    parser.add_argument("--clientport", type=int, default=defaultClientPort)
    parser.add_argument("--name", type=str, default="Example")
    args = parser.parse_args()

    Microservice = Microservice_main(
        serverIP=args.serverip,
        serverPort=args.serverport,
        clientIP=args.clientip,
        clientPort=args.clientport,
        microservice_name=args.name,
    )
    Microservice.microservice_run()

    #####使用方式2,直接运行#####
    # Microservice = Microservice_main(
    #     serverIP="localhost",
    #     serverPort=18000,
    #     microservice_name="Example_end",
    # )
    # Microservice.microservice_run()


if __name__ == "__main__":
    main()
