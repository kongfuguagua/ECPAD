import os
import socket
import time


class client(object):

    def __init__(self, clientIP, clientPort):  # 目前使用值传入，后续使用自动检测ip和port        self.__masterIP=masterIP
        self.sockclient = None
        self.socknameclient = None
        self.clientPort = clientPort
        self.clientIP = clientIP
        # self.client()

    def CreateClientSocket(self):
        while 1:
            try:
                self.sockclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sockclient.connect((self.clientIP, self.clientPort))
                self.SendOneSentence("client1")  # 先发个名字
                break
            except ConnectionRefusedError:
                print('由于目标计算机积极拒绝，无法连接')
                time.sleep(1)
            except Exception as e:
                print('client sock {} error: {}'.format(self.socknameclient, e))
                self.sockclient.close()
                # break

    def getIP(self):  # 打印IP、Port等信息
        print()

    def HandleClientConversation(self):
        try:
            for i in range(5):
                self.handle_request_client()
        except ConnectionRefusedError:
            print('由于目标计算机积极拒绝，无法连接')
            time.sleep(1)
        except Exception as e:
            print('client sock {} error: {}'.format(self.socknameclient, e))
            self.sockclient.close()
            # break

    def handle_request_client(self):
        self.SendFile('./dataset/0.png')

    def SendOneSentence(self, sentence):
        self.sockclient.sendall(sentence.encode())
        self.confirmOver()

    def SendFile(self, filename):
        if os.path.isfile(filename):  # 判断文件存在
            # 1.先发送文件大小，让客户端准备接收
            size = os.stat(filename).st_size  # 获取文件大小
            self.SendOneSentence(str(size))
            print('发送的大小：', size)
            self.SendOneSentence(os.path.basename(filename))  # 把文件名先发过去
            # 2.发送文件内容
            f = open(filename, 'rb')
            for line in f:
                self.sockclient.sendall(line)  # 发送数据
            f.close()
        else:  # 文件不存在情况
            self.sockclient.send('文件不存在'.encode("utf-8"))

    def recv_until(self, suffix):
        message = self.sockclient.recv(4096)
        if not message:
            raise EOFError('sock close')
        while not message.endswith(suffix):
            data = self.sockclient.recv(4096)
            if not data:
                raise EOFError('sock close')
            message += data
        return message

    def recvall(self, size=4096):
        data = b''
        while True:
            packet = self.sockclient.recv(size)
            data += packet
            if len(packet) < size:
                break
        return data

    def confirmOver(self):
        data = self.recvall()
        i = 0
        while data[-1] != 64:  # 64为@的ascii码
            i += 1
            time.sleep(0.01)
            data = self.recvall()
            if i > 50:
                raise Exception('无法确定接收状态')
        return True
