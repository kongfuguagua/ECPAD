import argparse
import json
import os
import threading
import time

from MQTT import Mqtt


class text_output(Mqtt):
    def __init__(self, subIP, subPort, deal_images="deal_images"):
        self.__dealType = deal_images
        Mqtt.__init__(self, subIP, subPort)

    def sub_topic(self):  # 订阅集合
        self.client.subscribe('text/sort')
        self.client.message_callback_add('text/sort', self.text_sort_handle)

    def text_sort_handle(self, client, userdata, msg):
        a = threading.Thread(target=self.text_sort_callback, args=(msg,))
        a.start()

    def text_sort_callback(self, msg):
        character_count = json.loads(msg.payload)
        count=self.print_sorted_characters(character_count)
        self.pub_topic(count)

    def print_sorted_characters(self,sorted_characters):
        print("字母出现次数排序：")
        for char, count in sorted_characters:
            if char != '#':
                print(f"{chr(int(char))}: {count}")
            else:
                return count

    def pub_topic(self, count):
        self.client.publish('time/text/output', str(count) + ' ' + str(time.time()))

    def main(self):
        self.mqtt_connect()
        self.sub_topic()
        self.sub_loop_forever()


if __name__ == "__main__":
    k8s = 1
    if k8s == 1:
        defaultIP = os.environ.get("MQTTBROKER001_SERVICE_HOST")
        defaultPort = os.environ.get("MQTTBROKER001_PORT_1883_TCP_PORT")
    else:
        defaultIP = '127.0.0.1'
        defaultPort = '1883'
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default=defaultIP)
    parser.add_argument('--port', type=int, default=int(defaultPort))
    parser.add_argument('--deal_index', type=str, default='dataset')
    args = parser.parse_args()
    pub = text_output(args.ip, args.port, args.deal_index)
    pub.main()