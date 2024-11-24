这是一个一条微服务链，包括3个构建镜像的基础文件。
mnist-input模拟链的起点，包括100张mnist图片，并通过tcp发送到下一个微服务。
mnist-infer是一个推理镜像，包括1个训练好的前向神经网络和tcp协议和http协议，时刻准备接收mnist图片，输出识别出的数字。
mnist-output是链的终点，包括一个flask架构设计的网页前后端，记录访问过的ip地址和次数，访问http://ip:port可以解析