FROM python:3.9.18-bullseye
WORKDIR /home/pv-infer
ADD . .
RUN pip install -r requirements.txt
WORKDIR /home/pv-infer/src
CMD ["python","./main.py"]