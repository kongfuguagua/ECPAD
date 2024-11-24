import argparse
import os
import pickle
import time
from MQTT import Mqtt
import pandas as pd
import json
import consulaccess
import random


class PV_pub(Mqtt):
    def __init__(self, clientIP, clientPort, filelistname):
        super(PV_pub, self).__init__(clientIP, clientPort)
        self.n_data = None
        self.input_data = None
        self.getimagesaddr(filelistname)
        self.count = 0
        # self.pw_enable = pw_enable
        # self.mqttuser = mqttuser
        # self.mqttpw = mqttpw

    def getimagesaddr(self, filepath):
        self.input_data = pd.read_csv(filepath, encoding="utf-8")
        self.n_data = len(self.input_data) / 40

    def pub_topic(self):
        while True:
            print("sending data number:", self.count % self.n_data)
            # fileidx = int(self.count % self.n_data)
            fileidx = random.randint(0, self.n_data - 1)
            dataslice = self.input_data.iloc[fileidx * 40 : (fileidx + 1) * 40].values.tolist()

            json_data = json.dumps(dataslice)

            msginfo = self.client.publish("mqttv1/pvdata/json", json_data)
            # msginfo = self.client.publish(topic="mqttv1", payload="amazing", qos=0, retain=False)
            try:
                msginfo.is_published()
            except:
                print("send failed")
            # 2.发送序列化数据
            self.count += 1
            time.sleep(5)

    def main(self):
        self.mqtt_connect()
        self.pub_topic()


def get_ip_port():
    consul = consulaccess.ConsulAccess(host="192.168.3.200", port="31995")
    services = consul.serach_service("iiip-mqttbroker001-utils")
    return services[0][0], services[0][1]


if __name__ == "__main__":
    # k8s = 0
    # if k8s == 1:
    #     defaultIP = os.environ.get("MY_POD_IP")
    #     defaultPort = os.environ.get("OUTPUT_SERVICE_PORT_OUTPUTSERVER")
    # else:
    #     defaultIP = "192.168.3.100"
    #     defaultPort = "1883"
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--ip", type=str, default=defaultIP)
    # parser.add_argument("--port", type=int, default=int(defaultPort))
    # parser.add_argument("--imageaddr", type=str, default="./pvdata.csv")
    # parser.add_argument("--pw_enable", type=bool, default=False)
    # # parser.add_argument("--mqttuser", type=str, default="root")
    # # parser.add_argument("--mqttpw", type=str, default="123456")
    # parser.add_argument("--mqttuser", type=str, default="")
    # parser.add_argument("--mqttpw", type=str, default="")
    # args = parser.parse_args()
    # pub = PV_pub(args.ip, args.port, args.imageaddr)
    ip, port = get_ip_port()
    print(ip)
    print(port)
    pub = PV_pub(ip, port, "./pvdata.csv")
    pub.main()

    # 看看是否需要加上一个断线重连的模块
