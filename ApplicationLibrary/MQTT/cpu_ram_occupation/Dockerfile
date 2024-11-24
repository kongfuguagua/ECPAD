FROM python:latest
WORKDIR /home/source
ADD . .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /home/source/src
CMD ["python","main.py"]