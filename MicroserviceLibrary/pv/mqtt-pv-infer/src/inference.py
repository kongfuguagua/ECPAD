import torch


class CNNnet(torch.nn.Module):
    def __init__(self):
        super(CNNnet, self).__init__()
        self.conv1 = torch.nn.Sequential(
            torch.nn.Conv2d(in_channels=1,  # 上一层输出维度的第二个数
                            out_channels=1,  # Cout
                            kernel_size=(4, 4),  # k=4*4
                            stride=1,  # ss
                            padding=0),  # p
            torch.nn.BatchNorm2d(1),  # BatchNorm2d传入的参数是channel的大小,等于out_channels
            torch.nn.ReLU()
        )
        self.conv2 = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels=1,
                            out_channels=3,
                            kernel_size=3,
                            stride=2,
                            padding=0),
            torch.nn.BatchNorm1d(3),
            torch.nn.ReLU()
        )
        self.conv3 = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels=3,
                            out_channels=5,
                            kernel_size=3,
                            stride=1,
                            padding=1),
            torch.nn.BatchNorm1d(5),
            torch.nn.ReLU()
        )
        self.MaxPool1 = torch.nn.Sequential(
            torch.nn.MaxPool1d(kernel_size=4, stride=2)
        )
        self.conv4 = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels=5,
                            out_channels=8,
                            kernel_size=3,
                            stride=1,
                            padding=1),
            torch.nn.BatchNorm1d(8),
            torch.nn.ReLU()
        )
        self.MaxPool2 = torch.nn.Sequential(
            torch.nn.MaxPool1d(kernel_size=2, stride=2)
        )
        self.conv5 = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels=8,
                            out_channels=16,
                            kernel_size=3,
                            stride=1,
                            padding=1),
            torch.nn.BatchNorm1d(16),
            torch.nn.ReLU()
        )
        self.MaxPool3 = torch.nn.Sequential(
            torch.nn.MaxPool1d(kernel_size=4, stride=1)
        )
        self.fc1 = torch.nn.Sequential(
            torch.nn.Linear(16, 10)
        )
        self.fc2 = torch.nn.Sequential(
            torch.nn.Linear(10, 9)
        )

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
        x = torch.max(x, 1)[1]
        return x

    def NNLoad(self):
        self.DEVICE = 'cpu'
        self.model = torch.load('./pv_infer.pth', map_location=torch.device(self.DEVICE))
        self.model.eval()


    def infer(self,input_x,label_y):
        test_x = torch.autograd.Variable(input_x).to(self.DEVICE).unsqueeze(0)
        test_y = torch.autograd.Variable(label_y).to(self.DEVICE)
        test_x = test_x.permute(0, 3, 1, 2)  # 调整输入维度
        out = self.model(test_x)
        self.predicted = out  # 使用类成员保存预测结果
        print('Infer value:', out.item(), 'True value:', test_y.item())
        infer_reference = 'Infer value:' + str(out), 'True value:' + str(test_y)
        return infer_reference

    def NNoutput(self):
        print(self.predicted)
