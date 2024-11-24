import argparse
import time
import os
from server import server
from flask import Flask, request

class MnistOutput(server):
    def __init__(self, masterIP, masterPort):
        super(MnistOutput, self).__init__(masterIP, masterPort)

    def handle_request_server(self, client_sock):
        sentence = self.recvall_confire(client_sock)
        print(sentence)

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    # 获取客户端 IP 地址
    client_ip = request.remote_addr

    # 获取链接次数，并增加计数
    if linkset.get(client_ip) is not None:
        linkset[client_ip] += 1
    else:
        linkset[client_ip] = 1
    link_count = linkset[client_ip]

    # 获取客户端发送的内容
    client_data = request.form.get('key', default='', type=str)

    return {
        "client_ip": client_ip,
        "link_count": link_count,
        "client_data": client_data,
        "all": str(linkset.items())
    }


if __name__ == '__main__':
    defaultIP=os.environ.get("MY_POD_IP")
    defaultPort=os.environ.get("OUTPUT_SERVICE_PORT_OUTPUTSERVER")
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default=defaultIP)
    parser.add_argument('--port', type=int, default=int(defaultPort))
    args = parser.parse_args()
    # server = MnistOutput(args.ip, args.port)
    # server.CreateServerSocket()
    # server.Accept_client()
    linkset = {args.ip + ':' + str(args.port): 0}
    app.run(host=args.ip, port=args.port)
