'''
All Model Structures
'''
import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class MLP(nn.Module):

    def __init__(self):
        super(MLP, self).__init__()
        self.layer1 = nn.Sequential(nn.Linear(290, 200), nn.ReLU(True))
        self.layer2 = nn.Sequential(nn.Linear(200, 100), nn.ReLU(True))
        self.layer4 = nn.Sequential(nn.Linear(100, 52), nn.ReLU(True))

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer4(x)
        return x


class DQN(nn.Module):

    def __init__(self,dim=498):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(dim, 380)
        self.fc2 = nn.Linear(380, 250)
        self.fc3 = nn.Linear(250, 100)
        self.fc4 = nn.Linear(100, 52)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        return x

        
class ConvFCNet(nn.Module):
    def __init__(self):
        super(ConvFCNet, self).__init__()
        self.decom = decom_layer()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=16, kernel_size=(5, 3), stride=1)
        self.pool1 = nn.MaxPool2d(kernel_size=(3, 1))
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=36, kernel_size=3, stride=1)
        self.pool2 = nn.MaxPool2d(kernel_size=2)
        self.conv_fc1 = nn.Sequential(nn.Linear(1764, 991), nn.BatchNorm1d(991))
        self.connect = connect_layer()
        self.fc1 = nn.Sequential(nn.Linear(1000, 256), nn.BatchNorm1d(256))
        self.fc2 = nn.Linear(256, 52)

    def forward(self, x):
        x, y = self.decom(x)
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        x = x.view(-1, 36 * 7 * 7)
        x = F.relu(self.conv_fc1(x))
        x = self.connect(x, y)
        x = self.fc2(F.relu(self.fc1(x)))
        return x
