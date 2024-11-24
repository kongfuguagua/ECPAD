import argparse
import os
import time
from client import client


class MnistInput(client):
    def __init__(self, masterIP, masterPort, filelistname):
        super(MnistInput, self).__init__(masterIP, masterPort)
        self.getimagesaddr(filelistname)
        self.count = 0
        self.CreateClientSocket()

    def handle_request_client(self):
        self.SendFile(os.path.abspath('./mnist_images/'+self.img_paths[self.count % self.n_data]))
        self.count += 1
        time.sleep(1)

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


if __name__ == '__main__':
    defaultIP=os.environ.get("INFERENCE_SERVICE_HOST")
    defaultServerPort=os.environ.get("INFERENCE_SERVICE_PORT_INPUTSERVER")
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default=defaultIP)
    parser.add_argument('--port', type=int, default=defaultServerPort)
    parser.add_argument('--imageaddr', type=str, default='./mnist_infer_label.txt')
    args = parser.parse_args()
    client = MnistInput(args.ip, args.port, args.imageaddr)
    client.HandleClientConversation()

