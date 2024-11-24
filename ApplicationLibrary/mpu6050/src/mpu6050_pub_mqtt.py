import time
import paho.mqtt.client as mqtt
import argparse
from MPU6050 import MPU
def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

def determineRotation(roll, pitch):
    if roll > 0:
        return "01"  # 顺时针旋转
    elif roll < 0:
        return "11"  # 逆时针旋转
    elif roll == 0 and pitch == 0:
        return "00"  # 不动
    else:
        return "10"  # 其他情况

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='172.17.0.2')
    parser.add_argument('--port', type=int, default=1883)
    parser.add_argument('--topic', type=str, default='mpu6050')
    args = parser.parse_args()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.ip,args.port, 600)
    
    # Set up class
    gyro = 250      # 250, 500, 1000, 2000 [deg/s]
    acc = 2         # 2, 4, 7, 16 [g]
    tau = 0.6
    mpu = MPU(gyro, acc, tau)

    # Set up sensor and calibrate gyro with N points
    mpu.setUp()
    mpu.calibrateGyro(500)

    # Run for 20 secounds
    # startTime = time.time()
    while(1):
        roll,pitch,yaw= mpu.compFilter()
        rotation_direction = determineRotation(roll, pitch)
        print(rotation_direction)
        time.sleep(0.1)
        client.publish(args.topic, payload=rotation_direction, qos=0)
