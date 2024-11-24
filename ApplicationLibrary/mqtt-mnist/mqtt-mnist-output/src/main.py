import argparse
import threading
import time
import os
from MQTT import Mqtt

class MnistOutput(Mqtt):
    def __init__(self, masterIP, masterPort):
        super(MnistOutput, self).__init__(masterIP, masterPort)

    def sub_topic(self):  # 订阅集合
        self.client.subscribe('result')
        self.client.message_callback_add('result', self.result_handle)  # 订阅回调

    def result_handle(self, client, userdata, msg):  # test主题回调
        a = threading.Thread(target=self.result_callback, args=(msg,))
        a.start()

    def result_callback(self, msg):  # json接收demo
        print('线程号：', threading.get_ident())
        print('{}:{}'.format(msg.topic,msg.payload))

    def main(self):
        self.mqtt_connect()
        self.sub_topic()
        self.sub_loop_forever()

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
    args = parser.parse_args()
    sub = MnistOutput(args.ip, args.port)
    sub.main()
