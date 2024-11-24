from torch import nn
import torch
from torchvision import datasets, transforms
from PIL import Image


class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()  # b 16,28,28深度、长、宽
        layer1 = nn.Sequential()
        layer1.add_module("conv1", nn.Conv2d(1, 16, 3))  # b 32 26 26深度、长、宽
        layer1.add_module("norm1",
                          nn.BatchNorm2d(16))  # 卷积层之后总会添加BatchNorm2d进行数据的归一化处理，这使得数据在进行Relu之前不会因为数据过大而导致网络性能的不稳定。
        layer1.add_module("relu1", nn.ReLU(True))
        self.layer1 = layer1

        layer2 = nn.Sequential()
        layer2.add_module("conv2", nn.Conv2d(16, 32, 3))  # b 32 24 24深度、长、宽
        layer2.add_module("norm2", nn.BatchNorm2d(32))
        layer2.add_module("relu2", nn.ReLU(True))
        layer2.add_module("pool2", nn.MaxPool2d(2, 2))  # b 32 12 12 深度、长、宽
        self.layer2 = layer2

        layer5 = nn.Sequential()
        layer5.add_module("fc1", nn.Linear(32 * 12 * 12, 1024))  # 128*4*4=2048
        layer5.add_module("fc_relu1", nn.ReLU(True))
        layer5.add_module("fc2", nn.Linear(1024, 128))
        layer5.add_module("fc_relu2", nn.ReLU(True))
        layer5.add_module("fc3", nn.Linear(128, 10))
        self.layer5 = layer5

    def forward(self, input_x):
        conv1 = self.layer1(input_x)
        conv2 = self.layer2(conv1)
        fc_input = conv2.view(conv2.size(0), -1)  # 高维数据 ‘压’成 低维数据
        fc_out = self.layer5(fc_input)  # 全连接层(低维数据)
        return fc_out

    def NNLoad(self):
        self.model = torch.load('model.pth')
        self.DEVICE = 'cpu'
        self.data_transforms = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.5], [0.5])])


    def infer(self,imgname):
        img = self.data_transforms(Image.open(imgname))
        with torch.no_grad():
            img = img.unsqueeze(0)
            class_output = self.model(img)
            _, self.predicted = torch.max(class_output.data, 1)
            self.NNoutput()

    def NNoutput(self):
        print(self.predicted)
