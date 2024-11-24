"""
本文件是数据的核心处理部分，用于将得到的数据进行处理
"""
import time


class Execution:
    def __init__(self):
        self.start_time = time.time()

    def run(self, data, client_name):
        """
        本函数是数据处理的核心函数，用于将数据进行处理
        :return: 处理后的数据
        """
        print("Received data: ", data, " at ", time.time() - self.start_time, "s")
        return data

    def multi_run(self, data):
        """
        本函数是多客户端数据联合处理的核心函数，用于将多个客户端的数据进行协同处理
        :return: 处理后的数据
        """
        return 0
