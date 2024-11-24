import os
import argparse
import time
from threading import Thread
from server import server
from client import client
from inference import batch_net
import requests

class server_infer(server, batch_net, client):
    def __init__(self, masterIP, masterPort, clientIP, clientPort, deal_images="deal_images"):
        self.__dealType = deal_images
        server.__init__(self, masterIP, masterPort)
        batch_net.__init__(self)
        self.NNLoad()
        client.__init__(self, clientIP, clientPort)

    def handle_request_server(self, client_sock):
        filename = self.preRevFile(client_sock,'./')
        print(filename)
        self.infer(filename)

    def handle_request_client(self):
        self.SendOneSentence(str(self.predicted.item()))

    def NNoutput(self):
        thread = Thread(target=self.http_client,args=(self.predicted.item(),'http://'+self.clientIP+':'+str(self.clientPort)))
        # 设置成守护线程
        thread.setDaemon(True)
        thread.start()

    def http_client(self,data_value,url='http://127.0.0.1:1800/'):
        data = {'key': data_value}
        response = requests.post(url, data=data)
        print(response.text)


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    defaultInferIP=os.environ.get("MY_POD_IP")
    defaultServerPort=os.environ.get("INFERENCE_SERVICE_PORT_INPUTSERVER")
    defaultOutputIP=os.environ.get("OUTPUT_SERVICE_HOST")
    defaultClientPort=os.environ.get("OUTPUT_SERVICE_PORT_OUTPUTSERVER")
    parser = argparse.ArgumentParser()
    parser.add_argument('--serverip', type=str, default=defaultInferIP)
    parser.add_argument('--serverport', type=int, default=int(defaultServerPort))
    parser.add_argument('--clientip', type=str, default=defaultOutputIP)
    parser.add_argument('--clientport', type=int, default=int(defaultClientPort))
    args = parser.parse_args()
    infer = server_infer(args.serverip, args.serverport, args.clientip, args.clientport)
    infer.CreateServerSocket()
    infer.Accept_client()
    # infer.CreateClientSocket()


