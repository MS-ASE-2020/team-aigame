

import numpy as np
import random
import math

from collections import deque, namedtuple
import itertools

Transition = namedtuple('Transition', ('state', 'action', 'reward', 'next_state'))

class ReplayMemory(object):

    def __init__(self, cap):
        self.cap = cap
        self.mem = []
        self.pos = 0

    def push(self, *args):
        if len(self.mem) < self.cap:
            self.mem.append(None)
        self.mem[self.pos] = Transition(*args)
        self.pos = (self.pos + 1) % self.cap

    def sample(self, num):
        return random.sample(self.mem, num)

    def __len__(self):
        return len(self.mem)