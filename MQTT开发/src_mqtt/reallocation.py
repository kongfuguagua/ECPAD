"""
runing.py -c 2 -t 0.01 -m 1000
-c cpu核数，不加-c参数为最大核数
-t cpu运算频率时间，间隔，越小占用越高
-m 内存占用，1000MB
"""
import time
import argparse
from multiprocessing import Process
from multiprocessing import cpu_count, Value

Counter = Value('i', 0)


def exec_func(bt, size):
    global Counter
    count = 0
    while count < size:
        for i in range(0, 1000):
            pass
        time.sleep(bt)
        count += 1
    Counter.value += 1
    print("进程执行完成")


def running(cpu_count=cpu_count(), cpu_sleep_time=1, test_size=1, memory=1000):
    _doc = """
                runing.py -c 2 -t 0.01 -m 1000
                -c 指定cpu核数，不加-c参数默认为当前cpu最大核数
                -t cpu运算频率时间，间隔，越小占用越高
                -m 内存占用，1000MB

                CPU使用率需要手动增加减少-t参数来达到，预期使用率。
               """
    print("\n====================使用说明=========================")
    print("{}".format(_doc))
    print("\n====================================================")
    print('\n当前占用CPU核数:{}'.format(cpu_count))
    # print('\n内存预计占用:{}MB'.format(memory_used_mb))
    print('\n资源浪费中......')

    try:
        # 内存占用
        s = ' ' * (memory * 1024)
    except MemoryError:
        print("剩余内存不足，内存有溢出......")

    try:
        start = time.perf_counter()
        ps_list = []
        for i in range(0, cpu_count):
            ps_list.append(Process(target=exec_func, args=(cpu_sleep_time, test_size,)))
        for p in ps_list:
            p.start()
        for p in ps_list:
            p.join()
        end = time.perf_counter()
        print("time:", end - start, "s")
        print("运行完毕")
    except KeyboardInterrupt:
        print("资源浪费结束!")

# if __name__ == "__main__":
#
#     parse = argparse.ArgumentParser(description='runing')
#     parse.add_argument("-c", "--count", default=cpu_count(), help='cpu count')
#     parse.add_argument("-t", "--time", default=1, help='cpu time')
#     parse.add_argument("-s", "--size", default=1, help='test size')
#     parse.add_argument("-m", "--memory", default=1000, help='memory')
#     args = parse.parse_args()
#     cpu_logical_count = int(args.count)
#     test_size = int(args.size)
#     memory_used_mb = int(args.memory)
#     try:
#         cpu_sleep_time = int(args.time)
#     except ValueError:
#         try:
#             cpu_sleep_time = float(args.time)
#         except ValueError as ex:
#             raise ValueError(ex)
#
#     running(cpu_logical_count,cpu_sleep_time,test_size,memory_used_mb)
