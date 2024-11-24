import argparse
import os
import pickle
import time
from MQTT import Mqtt


class PV_pub(Mqtt):
    def __init__(self, clientIP, clientPort, filelistname):
        super(PV_pub, self).__init__(clientIP, clientPort)
        self.n_data = None
        self.input_data = None
        self.getimagesaddr(filelistname)
        self.count = 0

    def getimagesaddr(self, filepath):
        with open(filepath, 'rb') as f:
            data_test = pickle.load(f)
        self.input_data = data_test
        self.n_data = len(data_test)


    def pub_topic(self):
        while True:
            print('sending data number:', self.count % self.n_data)
            fileidx = self.count % self.n_data
            dataline = self.input_data[fileidx]  # 取特定数据行, tuple = （input,label）
            # print(type(dataline))
            # 序列化tuple，将数据类型转化为字符串
            serialized_data = pickle.dumps(dataline)
            self.client.publish('pv', serialized_data)
            # 2.发送序列化数据
            self.count += 1
            time.sleep(1)

    def main(self):
        self.mqtt_connect()
        self.pub_topic()


if __name__ == '__main__':
    k8s = 0
    if k8s == 1:
        defaultIP = os.environ.get("MY_POD_IP")
        defaultPort = os.environ.get("OUTPUT_SERVICE_PORT_OUTPUTSERVER")
    else:
        defaultIP = '127.0.0.1'
        defaultPort = '1883'
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default=defaultIP)
    parser.add_argument('--port', type=int, default=int(defaultPort))
    parser.add_argument('--imageaddr', type=str, default='./PV_testset.pkl')
    args = parser.parse_args()
    pub = PV_pub(args.ip, args.port, args.imageaddr)
    pub.main()
