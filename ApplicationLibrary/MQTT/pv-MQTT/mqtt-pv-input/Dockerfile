FROM python:latest
WORKDIR /home/mnist-input
ADD . .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /home/mnist-input/src
CMD ["python","main.py"]