import os
import argparse
import time
from threading import Thread
from MQTT import Mqtt
from inference import batch_net


class server_infer(Mqtt, batch_net):
    def __init__(self,subIP, subPort, deal_images="deal_images"):
        self.__dealType = deal_images
        batch_net.__init__(self)
        Mqtt.__init__(self,subIP, subPort)
        self.NNLoad()

    def sub_topic(self):  # 订阅集合
        self.client.subscribe('mnist')
        self.client.message_callback_add('mnist', self.image_handle)

    def image_deal(self, filename):
        self.infer(filename)

    def NNoutput(self):
        print(self.predicted)
        self.pub_topic('result', self.predicted)

    def pub_topic(self, topic, ans):
        self.client.publish(topic, str(ans))

    def main(self):
        self.mqtt_connect()
        self.sub_topic()
        self.sub_loop_forever()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    k8s = 0
    if k8s == 1:
        defaultSubIP = os.environ.get("MY_POD_IP")
        defaultSubPort = os.environ.get("INFERENCE_SERVICE_PORT_INPUTSERVER")
    else:
        defaultSubIP = '127.0.0.1'
        defaultSubPort = '1883'

    parser = argparse.ArgumentParser()
    parser.add_argument('--subip', type=str, default=defaultSubIP)
    parser.add_argument('--subport', type=int, default=int(defaultSubPort))
    args = parser.parse_args()
    infer = server_infer(args.subip, args.subport)
    infer.main()
