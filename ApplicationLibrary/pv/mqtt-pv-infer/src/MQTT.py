import base64
import threading
import time
import paho.mqtt.client as mqtt
import os
import json


class Mqtt:
    def __init__(self, clientIP, clientPort):  # 目前使用值传入，后续使用自动检测ip和port        self.__masterIP=masterIP
        self.clientPort = clientPort
        self.clientIP = clientIP
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.image_index=0

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + ":" + str(msg.payload))

    def mqtt_connect(self):  # 链接MQTTbroker
        while 1:
            try:
                self.client.connect(self.clientIP, self.clientPort, 60)
                print('seccess')
                # self.SendOneSentence("client1")  # 先发个名字
                break
            except ConnectionRefusedError:
                print('由于目标计算机积极拒绝，无法连接')
                time.sleep(1)
            except Exception as e:
                print('client sock {} error: {}'.format((self.clientIP, self.clientPort), e))
                # break

    def pub_topic(self,*args,**kwargs):
        pass

    def image_preproess(self, filename, byte='high'):
        if os.path.isfile(filename):
            f = open(filename, "rb")
            fileContent = f.read()
            if byte == 'high':
                byteArr = bytes(fileContent)
            else:
                byteArr = base64.b64encode(fileContent)
        else:
            print('文件不存在')
            byteArr=None
        return byteArr

    def sub_topic(self):  # 订阅集合
        self.client.subscribe('test')
        self.client.message_callback_add('test', self.test_handle)# 订阅回调
        self.client.subscribe('image')
        self.client.message_callback_add('image', self.image_handle)

    def test_handle(self, client, userdata, msg):  # test主题回调
        a = threading.Thread(target=self.test_callback, args=(msg,))
        a.start()

    def image_handle(self, client, userdata, msg):  # test主题回调
        a = threading.Thread(target=self.image_callback, args=(msg,))
        a.start()

    def test_callback(self, msg):  # json接收demo
        print('线程号：', threading.get_ident())
        payload = json.loads(msg.payload)
        print(msg.topic)
        print(payload['name'])

    def image_callback(self, msg):  # 图片接收demo
        print('线程号：', threading.get_ident())
        filename=r'./{}.png'.format(self.image_index)
        f = open(filename, 'wb')
        self.image_index=(self.image_index+1)%100
        payload = msg.payload
        f.write(payload)
        f.close()
        print(msg.topic)
        self.image_deal(filename)

    def image_deal(self,filename):
        pass

    def sub_loop_forever(self):
        self.client.loop_forever()

    def main(self):
        self.mqtt_connect()
        pass