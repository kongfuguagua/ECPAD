import argparse
import os
import threading
import time
from MQTT import Mqtt


class text_stats(Mqtt):
    def __init__(self, subIP, subPort, deal_images="deal_images"):
        self.__dealType = deal_images
        Mqtt.__init__(self, subIP, subPort)

    def sub_topic(self):  # 订阅集合
        self.client.subscribe('text/input')
        self.client.message_callback_add('text/input', self.text_input_handle)

    def text_input_handle(self, client, userdata, msg):
        a = threading.Thread(target=self.text_input_callback, args=(msg,))
        a.start()

    def text_input_callback(self, msg):
        count, character = msg.payload.split(b':')
        character_count = self.count_characters(character, count)  # 写入编号
        self.pub_topic(character_count, count)

    def count_characters(self, characters, count):
        character_count = {'#': int(count)}
        for char in characters:
            if char in character_count:
                character_count[char] += 1
            else:
                character_count[char] = 1
        return character_count

    def pub_topic(self, msg, count):
        self.json_pub('text/stats', msg)
        self.client.publish('time/text/stats', str(count.decode()) + ' ' + str(time.time()))

    def main(self):
        self.mqtt_connect()
        self.sub_topic()
        self.sub_loop_forever()


if __name__ == "__main__":
    k8s = 1
    if k8s == 1:
        defaultIP = os.environ.get("MQTTBROKER002_SERVICE_HOST")
        defaultPort = os.environ.get("MQTTBROKER002_PORT_1883_TCP_PORT")
    else:
        defaultIP = '127.0.0.1'
        defaultPort = '1883'
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default=defaultIP)
    parser.add_argument('--port', type=int, default=int(defaultPort))
    parser.add_argument('--deal_index', type=str, default='dataset')
    args = parser.parse_args()
    pub = text_stats(args.ip, args.port, args.deal_index)
    pub.main()
