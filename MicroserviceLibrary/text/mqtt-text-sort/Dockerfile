FROM python:3.9.18-bullseye
WORKDIR /home/mnist-output
ADD . .
RUN pip install -r requirements.txt
WORKDIR /home/mnist-output/src
CMD ["python","main.py"]