FROM python:latest
ADD . /MPU6050
WORKDIR /MPU6050
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


ENTRYPOINT ["python3", "./src/mpu6050_pub_mqtt.py"]
