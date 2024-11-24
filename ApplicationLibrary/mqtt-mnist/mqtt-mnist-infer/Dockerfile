FROM python:3.9.18-bullseye
WORKDIR /home/mnist-infer
ADD . .
RUN pip install -r requirements.txt
WORKDIR /home/mnist-infer/src
CMD ["python","./main.py"]