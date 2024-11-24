from MQTT import Mqtt
from reallocation import running
import argparse
import os
from multiprocessing import cpu_count


class client_src(Mqtt):
    def __init__(self, clientIP, clientPort):
        super(client_src, self).__init__(clientIP, clientPort)

    def pub_topic(self, topic, ans):
        if isinstance(ans, str):
            pass
        else:
            ans = str(ans)
        self.client.publish(topic, ans)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='127.0.0.1')
    parser.add_argument('--port', type=int, default=1883)
    parser.add_argument("-c", "--count", default=cpu_count(), help='cpu count')
    parser.add_argument("-t", "--time", default=1, help='cpu time')
    parser.add_argument("-s", "--size", default=1, help='test size')
    parser.add_argument("-m", "--memory", default=1000, help='memory')
    parser.add_argument("-topic", default='self', help='all or self')
    parser.add_argument("-context", default=10, help='mqtt pub bytes /B')
    args = parser.parse_args()
    # mqtt参数部分
    my_pod_name = "main.py"
    my_pod_name = os.environ.get("HOSTNAME")
    topic = args.topic + '/' + my_pod_name
    pub_byte = int(args.context)
    context = str(pub_byte) + " " * (pub_byte * 1024)
    pub_byte = int(args.context)
    # 浪费资源部分
    cpu_logical_count = int(args.count)
    test_size = int(args.size)
    memory_used_mb = int(args.memory)
    try:
        cpu_sleep_time = int(args.time)
    except ValueError:
        try:
            cpu_sleep_time = float(args.time)
        except ValueError as ex:
            raise ValueError(ex)
    # 主函数
    client_mqtt = client_src(args.ip, args.port)
    client_mqtt.mqtt_connect()
    try:
        while 1:
            client_mqtt.pub_topic(topic, pub_byte)
            running(cpu_logical_count, cpu_sleep_time, test_size, memory_used_mb)
    except KeyboardInterrupt:
        print("stop")
