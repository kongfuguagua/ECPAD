from torch import nn
import torch
from torchvision import datasets, transforms
from PIL import Image


class batch_net(nn.Module):
    def __init__(self, input_size=28 * 28, hidden_size1=300, hidden_size2=100, num_classes=10):
        super(batch_net, self).__init__()
        self.img = None
        self.data_transforms = None
        self.DEVICE = None
        self.model = None
        self.predicted = None
        self.fc1 = nn.Linear(input_size, hidden_size1)  # 输入层，线性（liner）关系
        self.relu = nn.ReLU()  # 隐藏层，使用ReLU函数
        self.fc11 = nn.Linear(hidden_size1, hidden_size2)  # 输入层，线性（liner）关系
        self.relu2 = nn.ReLU()  # 隐藏层，使用ReLU函数
        self.fc2 = nn.Linear(hidden_size2, num_classes)  # 输出层，线性（liner）关系

    # forword 参数传递函数，网络中数据的流动
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc11(out)
        out = self.relu2(out)
        out = self.fc2(out)
        return out

    def NNLoad(self):
        self.model = torch.load('model.pkl')
        self.DEVICE = 'cpu'
        self.data_transforms = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.5], [0.5])])


    def infer(self,imgname):
        img = self.data_transforms(Image.open(imgname))
        with torch.no_grad():
            t_img = img.view(-1, 28 * 28).to(self.DEVICE)
            class_output = self.model(t_img)
            _, self.predicted = torch.max(class_output.data, 1)
            self.NNoutput()

    def NNoutput(self):
        print(self.predicted)
