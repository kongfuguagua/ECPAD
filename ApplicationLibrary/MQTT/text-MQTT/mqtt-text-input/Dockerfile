FROM python:3.9.18-bullseye
WORKDIR /home/mnist-input
ADD . .
RUN pip install -r requirements.txt
WORKDIR /home/mnist-input/src
CMD ["python","main.py"]