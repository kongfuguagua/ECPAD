# 定义网络结构
import torch
from torch.autograd import Variable
import numpy as np
import matplotlib.pyplot as plt


class CNNnet(torch.nn.Module):
    def __init__(self):
        super(CNNnet, self).__init__()
        self.conv1 = torch.nn.Sequential(
            torch.nn.Conv2d(
                in_channels=1, out_channels=1, kernel_size=(4, 4), stride=1, padding=0  # 上一层输出维度的第二个数  # Cout  # k=4*4  # ss
            ),  # p
            torch.nn.BatchNorm2d(1),  # BatchNorm2d传入的参数是channel的大小,等于out_channels
            torch.nn.ReLU(),
        )
        self.conv2 = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels=1, out_channels=3, kernel_size=3, stride=2, padding=0), torch.nn.BatchNorm1d(3), torch.nn.ReLU()
        )
        self.conv3 = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels=3, out_channels=5, kernel_size=3, stride=1, padding=1), torch.nn.BatchNorm1d(5), torch.nn.ReLU()
        )
        self.MaxPool1 = torch.nn.Sequential(torch.nn.MaxPool1d(kernel_size=4, stride=2))
        self.conv4 = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels=5, out_channels=8, kernel_size=3, stride=1, padding=1), torch.nn.BatchNorm1d(8), torch.nn.ReLU()
        )
        self.MaxPool2 = torch.nn.Sequential(torch.nn.MaxPool1d(kernel_size=2, stride=2))
        self.conv5 = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels=8, out_channels=16, kernel_size=3, stride=1, padding=1), torch.nn.BatchNorm1d(16), torch.nn.ReLU()
        )
        self.MaxPool3 = torch.nn.Sequential(torch.nn.MaxPool1d(kernel_size=4, stride=1))
        self.fc1 = torch.nn.Sequential(torch.nn.Linear(16, 16))
        self.fc2 = torch.nn.Sequential(torch.nn.Linear(16, 16))

        # self.softmax = torch.nn.Softmax(self.fc2,dim=1)

        # self.softmax = torch.nn.Sequential(
        # torch.nn.Softmax()
        # )

    def forward(self, x):
        x = self.conv1(x)
        x = torch.squeeze(x, dim=-1)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.MaxPool1(x)
        x = self.conv4(x)
        x = self.MaxPool2(x)
        x = self.conv5(x)
        x = self.MaxPool3(x)
        x = self.fc1(x.view(x.size(0), -1))
        x = self.fc2(x)
        # x = self.softmax(x)
        return x


def infer(pv_data: np.ndarray, pv_temperature: float, pv_irradiance: float):
    # 转化数据类型
    input_test_pre = Variable(torch.from_numpy(pv_data))
    input_test_pre = input_test_pre.float()

    # 维度扩增
    input_test_pre = input_test_pre.unsqueeze(0).unsqueeze(-1)  # 将测试数据的维度从[n,40,4]扩充为[n,40,4,1]

    model = CNNnet()
    model = torch.load("./pv_infer.pth")
    model = model.cpu()
    model.eval()
    test_x = Variable(input_test_pre)
    test_x = test_x.permute(0, 3, 1, 2)  # 调整输入维度
    out = model(test_x)
    result = torch.max(out, 1)[1].numpy()

    # 定义一个字典，将数字和对应的状态进行映射
    status_mapping = {0: "正常状态", 1: "遮挡故障", 2: "老化故障", 3: "短路故障", 4: "开路故障"}

    # 测试数据
    for num in result:
        status = status_mapping.get(num, "未知状态")

    # 数据转换
    pv_temperature = float(pv_temperature)
    pv_temperature = str(pv_temperature)

    pv_irradiance = float(pv_irradiance)
    pv_irradiance = str(pv_irradiance)

    # 将二维数组转换为图像
    IV_data = pv_data[:, :2]
    # 绘制曲线
    plt.plot(IV_data[:39, 0], IV_data[:39, 1])
    plt.savefig("IV_curve.png")
    # plt.show()

    # 打开JPEG文件并读取内容
    with open("./IV_curve.png", "rb") as file:
        IV_curve = file.read()

    return status, pv_temperature, pv_irradiance, IV_curve
