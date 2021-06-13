import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

class DQN(nn.Module):

    def __init__(self, dim=498):
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


