FROM python:latest
WORKDIR /home/mnist-infer
ADD . .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /home/mnist-infer/src
CMD ["python","./main.py"]