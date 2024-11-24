import consulaccess
import redis
import numpy as np
from infer import infer, CNNnet
import warnings
import time

warnings.filterwarnings("ignore")


def main():
    consul_client = consulaccess.ConsulAccess(host="192.168.3.200", port="31995")
    services = consul_client.serach_service("iiip-redis-core")

    r = redis.Redis(host=services[0][0], port=services[0][1], db=0)

    last_timestamp = 0
    while True:
        latest_element = r.zrevrange("pvdata/json", 0, 0, withscores=True)

        for element, score in latest_element:
            data_str = element.decode("utf-8")
            data_list = eval(data_str)
            pv_data = np.array(data_list)
            pv_irradiance = pv_data[0, 2]
            pv_temperature = pv_data[0, 3]
            stamp = score
        if stamp == last_timestamp:
            time.sleep(1)
            continue
        else:
            print("New data received, time: ", stamp)
            last_timestamp = stamp

        status, pv_temperature_output, pv_irradiance_output, IV_curve = infer(pv_data, pv_temperature, pv_irradiance)
        # # 要发送的数据
        r.zadd("test/pvinfer/irradiance/string", {pv_irradiance_output: stamp})
        r.zadd("test/pvinfer/temperature/string", {pv_temperature_output: stamp})
        r.zadd("test/pvinfer/status/string", {status: stamp})

        # Delete the entire sorted set
        # result = r.delete("test/pvinfer/IV/png")
        # r.zadd("test/pvinfer/IV/png", {IV_curve: stamp})


if __name__ == "__main__":
    main()
