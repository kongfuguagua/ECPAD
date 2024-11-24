import os
import socket
from threading import Thread



class server(object):
    numOfConnect = 0  # 从机数量

    def __init__(self, masterIP, masterPort):  # 目前使用值传入，后续使用自动检测ip和port        self.__masterIP=masterIP
        self.listener = None
        self.dic_client_ipport = {}
        self.__masterPort = masterPort
        self.__masterIP = masterIP
        # self.CreateServerSocket()

    def getIP(self, name):  # 打印IP、Port等信息
        print(name + ':' + self.dic_client_ipport[name])

    def CreateServerSocket(self):  # TCP第一次握手
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置服务器断开连接时端口即可释放
        self.listener.bind((self.__masterIP, self.__masterPort))  # 映射一个套件字端口
        self.listener.listen(5)  # 设置sock为监听套接字，也暗示这个程序是一个服务器。调用listen后套接字属性无法改变，不能再发送数据或接受数据
        print('listen at', self.listener.getsockname())  # getsockname获得本地ip和port
        self.dic_client_ipport['server'] = self.listener.getsockname()

    def Accept_client(self):
        while 1:
            client_sock, client_addr = self.listener.accept()  # 只有客户端connect后accept才执行否则一直阻塞。sock是监听套接字，服务端调用accept后返回一个新的链接套接字sc，sc负责管理对话
            self.numOfConnect += 1
            print("accept connection from {},numOfConnect={}".format(client_addr,
                                                                     self.numOfConnect))  # sockname是新的链接套接字sc的ip和port
            thread = Thread(target=self.HandleServerConversation, args=(client_sock, client_addr))
            # 设置成守护线程
            thread.setDaemon(True)
            thread.start()

    def HandleServerConversation(self, client_sock, client_addr):  # 处理程序句柄 类似stm32hal库，套个马甲
        name = None
        try:
            name = self.recvall_confire(client_sock).decode(encoding='utf-8')  # 先收个名字，记录在案
            self.dic_client_ipport[name] = client_addr
            while 1:
                self.handle_request_server(client_sock)
        except EOFError:
            print('client sock to {} closed'.format(client_addr))
        except Exception as e:
            print('client sock {} error: {}'.format(client_addr, e))
        finally:
            if name is not None:
                self.dic_client_ipport.pop(name)
            self.RemoveClient(client_sock)

    def handle_request_server(self, client_sock):  # 服务函数
        self.preRevFile(client_sock)

    def preRevFile(self, client_sock):
        fileaddr = ''  # 处理文件地址
        filename=self.RevFile(client_sock, fileaddr)
        return fileaddr+filename

    def RevFile(self, client_sock, fileaddr):
        # 1.先接收长度，如果接收长度报错，说明文件不存在
        server_response = self.recvall_confire(client_sock)
        try:
            file_size = int(server_response.decode("utf-8"))
        except ValueError:
            raise ValueError('文件不存在')
        print('接收到的大小：', file_size)
        # 2.接收文件内容
        filename = str(self.recvall_confire(client_sock), encoding="utf-8")
        f = open(fileaddr + filename, 'wb')
        received_size = 0
        while received_size < file_size:
            size = 0  # 准确接收数据大小，解决粘包
            if file_size - received_size > 1024:  # 多次接收
                size = 1024
            else:  # 最后一次接收完毕
                size = file_size - received_size
            data = client_sock.recv(size)  # 多次接收内容，接收大数据
            data_len = len(data)
            received_size += data_len
            print('已接收：', int(received_size / file_size * 100), "%")
            f.write(data)
        f.close()
        return filename

    def recv_until(self, sock, suffix):
        message = sock.recv(4096)
        if not message:
            raise EOFError('sock close')
        while not message.endswith(suffix):
            data = sock.recv(4096)
            if not data:
                raise EOFError('sock close')
            message += data
        return message

    def recvall_confire(self, sock, size=4096):
        data = b''
        while True:
            packet = sock.recv(size)
            data += packet
            if len(packet) < size:
                break
        sock.send(b'@')  # 确认收到
        return data

    def RemoveClient(self, client_sock):
        self.numOfConnect -= 1
        client_sock.close()