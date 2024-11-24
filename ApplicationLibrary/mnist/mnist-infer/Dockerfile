FROM python:3.9.18-bullseye
WORKDIR /home/mnist-infer
ADD . .
RUN pip install -r requirements.txt
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
WORKDIR /home/mnist-infer/src
CMD ["python","./main.py"]