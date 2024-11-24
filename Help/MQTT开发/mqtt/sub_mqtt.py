from MQTT import Mqtt
import argparse
import os


class pub_mqtt(Mqtt):
    def __init__(self, clientIP, clientPort):
        super(pub_mqtt, self).__init__(clientIP, clientPort)

    def main(self):
        self.mqtt_connect()
        self.pub_topic()


class sub_mqtt(Mqtt):
    def __init__(self, clientIP, clientPort):
        super(sub_mqtt, self).__init__(clientIP, clientPort)

    def main(self):
        self.mqtt_connect()
        self.sub_topic()

    def sub_loop_forever(self):
        self.client.loop_forever()


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
    sub = sub_mqtt(args.ip, args.port)
    pub = pub_mqtt(args.ip, args.port)
    sub.main()
    # pub.main()
    sub.sub_loop_forever()
