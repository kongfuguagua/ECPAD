import os
import argparse
import pickle
import threading
import time
from MQTT import Mqtt
from inference import CNNnet


class server_infer(Mqtt, CNNnet):
    def __init__(self, subIP, subPort, deal_images="deal_images"):
        self.__dealType = deal_images
        CNNnet.__init__(self)
        Mqtt.__init__(self, subIP, subPort)
        self.NNLoad()

    def sub_topic(self):  # 订阅集合
        self.client.subscribe('pv')
        self.client.message_callback_add('pv', self.pv_handle)

    def pv_handle(self, client, userdata, msg):  # test主题回调
        a = threading.Thread(target=self.pv_callback, args=(msg,))
        a.start()

    def pv_callback(self, msg):  # json接收demo
        self.input_data, self.label = pickle.loads(msg.payload)
        # data = pickle.load(open(data,"rb"), e+ncoding='iso-8859-1')
        print("Input data: ", self.input_data, "True value: ", self.label)
        self.predicted = self.infer(self.input_data, self.label)
        self.NNoutput()

    def NNoutput(self):
        self.pub_topic('pv_result', self.predicted)

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
