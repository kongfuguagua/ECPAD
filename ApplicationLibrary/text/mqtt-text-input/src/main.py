import argparse
import time
from MQTT import Mqtt
import os

class text_input(Mqtt):
    def __init__(self,subIP, subPort, deal_index="dataset"):
        self.dealType = deal_index
        Mqtt.__init__(self,subIP, subPort)
        self.files = [dir for dir in self.get_files_from_directory(self.dealType)]
        self.count=0

    def extract_characters(self,filename):
        try:
            with open(filename, 'r') as file:
                text = file.read()
                # 仅保留英文字符并转换为小写
                characters = [char.lower() for char in text if char.isalpha()]
                characters_string = ''.join(characters)
                return characters_string
        except FileNotFoundError:
            print("文件未找到！")
        except Exception as e:
            print(e)

    def get_files_from_directory(self,directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                yield os.path.join(root, file)

    def pub_topic(self):
        while 1:
            characters=str(self.count)+":"+self.extract_characters(self.files[self.count%len(self.files)])
            self.count += 1
            if characters:
                self.client.publish('text/input', characters)
                self.client.publish('time/text/input', str(self.count)+' '+str(time.time()))
                time.sleep(1)

    def main(self):
        self.mqtt_connect()
        self.pub_topic()

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
    pub = text_input(args.ip, args.port, args.deal_index)
    pub.main()