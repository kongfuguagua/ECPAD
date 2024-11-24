"""
客户端和服务器的TCP通讯,版本v1.0
"""

import os
import socket
import time
from threading import Thread
from typing import Union


class Client(object):
    def __init__(self, clientIP, clientPort, clientName):
        """
        目前使用值传入,后续使用自动检测ip和port        self.__serverIP=serverIP
        """
        self.sock_client = None
        self.sock_name_client = None
        self.clientPort = clientPort
        self.clientIP = clientIP
        self.clientName = clientName

    ########################内部函数，不可继承#######################

    def __create_client_socket(self) -> None:
        """
        创建客户端套接字
        """
        while 1:
            try:
                self.sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock_client.connect((self.clientIP, self.clientPort))
                self.__send_one_sentence(self.clientName)  # 先发个名字
                break
            except ConnectionRefusedError:
                print("由于目标计算机积极拒绝，无法连接")
                time.sleep(1)
            except Exception as e:
                print("client sock {} error: {}".format(self.sock_name_client, e))
                self.sock_client.close()
                # break

    def __handle_client_conversation(self) -> None:
        """
        客户端建立连接,并发送指定的数据
        """
        try:
            for _ in range(5):  # TODO:why 5
                self.handle_request_client()
        except ConnectionRefusedError:
            print("由于目标计算机积极拒绝，无法连接")
            time.sleep(1)
        except Exception as e:
            print("client sock {} error: {}".format(self.sock_name_client, e))
            self.sock_client.close()
            # break

    def __recv_until(self, suffix) -> bytes:
        """
        接收数据直到遇到指定的标志位
        """
        message = self.sock_client.recv(4096)
        if not message:
            raise EOFError("sock close")
        while not message.endswith(suffix):
            data = self.sock_client.recv(4096)
            if not data:
                raise EOFError("sock close")
            message += data
        return message

    def __recv_all(self, sock: socket.socket, data_size: int = None, size: int = 1024, confirm: bool = False) -> bytes:
        """
        高度定义化的接收函数，可以根据需要接收数据，可以已知长度，可以未知长度（会导致粘包），可以指定是否有确认等进行修改
        """
        received_data = b""
        while True:
            data = sock.recv(size)
            received_data += data

            # 按照是否有指定长度给出接收跳出的方式
            if data_size is not None:
                if len(received_data) == data_size:
                    break
            else:
                if len(data) < size:
                    break
            print("已接收：", int(len(received_data) / data_size * 100), "%")
        if confirm:
            sock.send(b"@")  # 确认收到
        return received_data

    def __confirm_over(self) -> bool:
        """
        用于接收成功发送消息,若成功发送，则会收到一个@符号
        """
        data = self.__recv_all(self.sock_client, size=4096)
        i = 0
        while data[-1] != 64:  # 64为@的ascii码
            i += 1
            time.sleep(0.01)
            data = self.__recv_all(self.sock_client, size=4096)
            if i > 50:
                raise Exception("无法确定接收状态")
        return True

    def __send_one_sentence(self, sentence: str, confirm: bool = True) -> None:
        """
        单条消息的发送，需要确认接收
        """
        self.sock_client.sendall(sentence.encode())
        if confirm:
            self.__confirm_over()

    #####################可访问继承函数###########################

    def start_client(self) -> None:
        """
        解决方案略显简单,需要重构
        """
        self.__create_client_socket()
        # self.__handle_client_conversation()
        thread = Thread(target=self.__handle_client_conversation)
        # 设置成守护线程
        thread.setDaemon(True)
        thread.start()

    def handle_request_client(self):
        """
        这里是发送数据的核心模块，需要在主体部分进行实现
        """
        return
        self.send_file("./dataset/0.png")

    def get_IP(self) -> None:
        """
        打印IP、Port等信息
        """
        print("clientIP:" + str(self.clientIP) + " clientPort:" + str(self.clientPort))

    ###################各种数据的发送封装###################
    """
    理论上这里只应该留存基本的数据发送，封装应该放在主体部分进行，但是为了代码复用率能高一些，这部分函数就放在这里了，后面可以重用。如果需要发送新的数据形式，这里面已有的函数又无法满足的话，可以增加新的发送函数
    """

    def encode(self, data: str) -> bytes:
        """
        对数据进行编码,这只是一个例程，需要自己实现
        将要发送给的数据编码成为字符串，用于发送
        """
        return data.encode()

    def send_data(self, data, data_type: str = "str", **args) -> None:
        """
        发送数据，其中发送流程为：先发送数据长度，再发送数据类型，然后实际发送数据
        """
        # 编码数据,data可以是任意类型
        encoded_data = self.encode(data)

        # 发送数据长度
        self.__send_one_sentence(str(len(encoded_data)))

        # 发送数据类型
        self.__send_one_sentence(data_type)

        if data_type == "file":
            # 发送文件
            self.__send_one_sentence(args["filename"])

        # 发送数据
        self.sock_client.sendall(encoded_data)

    def send_file(self, filepath: str) -> None:
        """
        将send_data进行了进一步封装,可以直接根据文件路径发送文件,省掉了文件处理的过程
        """
        if os.path.isfile(filepath):  # 判断文件存在
            # 文件名
            filename = os.path.basename(filepath)
            filedata = ""
            f = open(filepath, "rb")
            for line in f:
                filedata += line.decode("utf-8")
            f.close()
            self.send_data(data=filedata, data_type="file", filename=filename)
        else:  # 文件不存在情况
            raise ValueError("文件不存在")


class Server(object):
    """
    TCP服务器模块,用于作为服务端监听连接请求接收数据
    """

    def __init__(self, serverIP, serverPort):
        """
        目前使用值传入,后续使用自动检测ip和port  self.__serverIP=serverIP
        """
        self.__serverPort = serverPort
        self.__serverIP = serverIP

        self.listener = None
        self.dic_client_ipport = {}
        self.number_of_connect = 0  # 从机数量
        # self.__create_server_socket()

    ##########################私有函数，无法继承#######################

    def __create_server_socket(self) -> None:
        """
        TCP第一次握手
        """
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 设置服务器断开连接时端口即可释放
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 映射一个套件字端口
        self.listener.bind((self.__serverIP, self.__serverPort))

        # 设置sock为监听套接字，也暗示这个程序是一个服务器。调用listen后套接字属性无法改变，不能再发送数据或接受数据,5表示最大连接数
        self.listener.listen(5)

        # getsockname获得本地ip和port
        print("listen at", self.listener.getsockname())
        self.dic_client_ipport["server"] = self.listener.getsockname()

    def __accept_client(self) -> None:
        """只有客户端connect后accept才执行否则一直阻塞。sock是监听套接字,服务端调用accept后返回一个新的链接套接字sc,sc负责管理对话"""
        while 1:
            client_sock, client_addr = self.listener.accept()
            self.number_of_connect += 1
            # sockname是新的链接套接字sc的ip和port
            print("accept connection from {},self.number_of_connect={}".format(client_addr, self.number_of_connect))
            thread = Thread(target=self.__handle_server_conversation, args=(client_sock, client_addr))
            # 设置成守护线程
            thread.setDaemon(True)
            thread.start()

    def __handle_server_conversation(self, client_sock: socket.socket, client_addr: str) -> None:
        """
        处理程序句柄 类似stm32hal库,套个马甲,运行在多线程中，对外是封闭的，不暴露其具体实现模式
        """
        name = None
        try:
            name = self.__recv_all(client_sock, size=4096, confirm=True).decode(encoding="utf-8")  # 先收个名字，记录在案
            self.dic_client_ipport[name] = client_addr
            while 1:
                self.handle_request_server(client_sock, name)
        except EOFError:
            print("client sock to {} closed".format(client_addr))
        except Exception as e:
            print("client sock {} error: {}".format(client_addr, e))
        finally:
            if name is not None:
                self.dic_client_ipport.pop(name)
            self.__remove_client(client_sock)

    def __recv_all(self, sock: socket.socket, data_size: int = None, size: int = 1024, confirm: bool = False) -> bytes:
        """
        高度定义化的接收函数，可以根据需要接收数据，可以已知长度，可以未知长度（会导致粘包），可以指定是否有确认等进行修改
        """
        received_data = b""
        while True:
            data = sock.recv(size)
            received_data += data

            # 按照是否有指定长度给出接收跳出的方式
            if data_size is not None:
                if len(received_data) == data_size:
                    break
                elif data_size - len(received_data) < size:
                    size = data_size - len(received_data)
            else:
                if len(data) < size:
                    break
            print("已接收：", int(len(received_data) / data_size * 100), "%")
        if confirm:
            sock.send(b"@")  # 确认收到
        return received_data

    def __remove_client(self, client_sock: socket.socket) -> None:
        """
        移除已连接的客户端
        """
        self.number_of_connect -= 1
        client_sock.close()

    #####################可访问继承函数###########################
    def decode(self, data: bytes) -> str:
        """
        对数据进行解码,这只是一个例程，需要自己实现
        将接收到的数据解码成为字符串，用于数据处理
        """
        return data.decode()

    def get_IP(self, name: str) -> None:
        """
        打印IP、Port等信息
        """
        print(name + ":" + self.dic_client_ipport[name])

    def start_server(self) -> None:
        """
        服务器启动函数，用于启动服务器
        """
        self.__create_server_socket()
        self.__accept_client()

    def handle_request_server(self, client_sock, client_name: str) -> None:
        """
        处理接收的数据在这个位置，后续修改主要就是这里,需要在主体部分进行实现
        """
        pass

    def receive_data(self, client_sock: socket.socket, **kwargs) -> Union[bytes, str]:
        """
        接收数据，其中接收流程为：先接收数据长度，再接收数据类型，然后实际接收数据
        """
        # 接收数据长度，如果接收长度报错，说明数据不存在
        server_response = self.__recv_all(client_sock, size=4096, confirm=True)
        try:
            data_size = int(server_response.decode("utf-8"))
        except ValueError:
            raise ValueError("数据不存在")

        # 接收数据类型，可以根据数据类型有一定程度的预处理
        data_type = str(self.__recv_all(client_sock, size=4096, confirm=True), encoding="utf-8")
        if data_type == "file":
            # 接收文件,不同于基本的数据接收，文件接收需要先接收文件名
            filename = str(self.__recv_all(client_sock, size=4096, confirm=True), encoding="utf-8")
            f = open(kwargs["fileaddr"] + filename, "wb")
        elif data_type == "str":
            # 接收字符串
            pass
        else:
            raise ValueError("数据类型不在库中，请检查或添加")

        # 接收数据
        received_data = self.__recv_all(client_sock, data_size=data_size)

        if data_type == "file":
            f.write(received_data)
            f.close()
            return filename

        decoded_data = self.decode(received_data)
        return decoded_data

    # TODO:，目前发送只有发送方的主动控制，接收方如果达到了承载能力可能接收缓冲区会被冲爆。等遇到这种情况的时候该文件需要进行调整以适应接收方的承载能力
    # TODO: 目前断联的时候发送应该如何处理还没有搞定，发送扔到缓存里面或者是直接丢弃
