import argparse
import os
import time
from MQTT import Mqtt


class Mnist_pub(Mqtt):
    def __init__(self, clientIP, clientPort, filelistname):
        super(Mnist_pub, self).__init__(clientIP, clientPort)
        self.getimagesaddr(filelistname)
        self.count = 0

    def getimagesaddr(self, filelistname):
        f = open(filelistname, 'r')
        data_list = f.readlines()
        f.close()

        self.n_data = len(data_list)

        self.img_paths = []
        self.img_labels = []

        for data in data_list:
            self.img_paths.append(data[:-3])
            self.img_labels.append(data[-2])

    def pub_topic(self):
        while 1:
            image_data = self.image_preproess(
                os.path.abspath('./mnist_images/' + self.img_paths[self.count % self.n_data]))
            self.count += 1
            self.client.publish('mnist', image_data)
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
    parser.add_argument('--imageaddr', type=str, default='./mnist_infer_label.txt')
    args = parser.parse_args()
    pub = Mnist_pub(args.ip, args.port, args.imageaddr)
    pub.main()
