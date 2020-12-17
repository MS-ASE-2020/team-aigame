import torch
import copy
import json
import tqdm
import random
import numpy as np
import pandas as pd
import torch.nn as nn
import torch.optim as optim
from pandas import DataFrame
import torch.nn.functional as F
import protobuf.protobuf_modify.message_pb2 as message
from protobuf.protobuf_modify.message_pb2 import GameState, TrickHistory
from socket import *
import threading
from util import GameState2feature_cnn

HOST = '127.0.0.1'
PORT = 6006
BUFSIZ = 1024
ADDR = (HOST, PORT)


class decom_layer(nn.Module):
    def __init__(self):
        super(decom_layer, self).__init__()

    def forward(self, x):
        return x[:, :988].reshape(x.shape[0], 1, 52, 19), x[:, 988:]


class connect_layer(nn.Module):
    def __init__(self):
        super(connect_layer, self).__init__()

    def forward(self, y, x):
        return torch.cat((y, x), dim=1)


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


def GameState2feature(game_state: GameState):
    round_index_feature = [0] * 13
    # round_index
    contract = game_state.contract
    bidding_feature = [0] * 12
    bidding_feature[contract.suit+7] = 1
    bidding_feature[contract.level] = 1
    dun_count_feature = [0] * 2
    desktop_cards_feature = [0] * 52
    remaining_cards_feature = [0] * 52
    round_out_cards_feature = [0] * 52
    open_hand_feature = [0] * 52
    hand_card_feature = [0] * 52
    identity = [0] * 3
    who = game_state.who
    dict_map = {0:0,1:2,2:1,3:2}
    identity[dict_map[who]] = 1
    playHistorys = game_state.playHistory
    round_index_feature[len(playHistorys)-1] = 1
    if len(playHistorys) == 0:
        pass
    else:
        for index, history in enumerate(playHistorys):
            # dun count
            if index != 0 and (history.lead == who or history.lead == (who+2) % 4):
                dun_count_feature[who % 2] += 1
            elif index != 0:
                dun_count_feature[(who + 1) % 2] += 1
            else:
                pass

            # desktop_cards_feature
            for card in history.cards:
                desktop_cards_feature[card.suit * 13 + card.rank] = 1

            # round_out_cards
            if index == len(playHistorys) - 1:
                for card in history.cards:
                    round_out_cards_feature[card.suit * 13 + card.rank] = 1
    for card in game_state.hand:
        hand_card_feature[card.suit * 13 + card.rank] = 1

    for card in game_state.dummy:
        open_hand_feature[card.suit * 13 + card.rank] = 1

    sum_card_feature = np.asarray(hand_card_feature) + np.asarray(open_hand_feature) + np.asarray(desktop_cards_feature)
    remaining_cards_feature = list(np.asarray([1]*52) - sum_card_feature)
    cat_feature = round_index_feature + bidding_feature + dun_count_feature + identity + hand_card_feature + open_hand_feature + desktop_cards_feature + remaining_cards_feature + round_out_cards_feature
    return cat_feature


class clientThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID, name, counter, tcpCliSock):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.tcpCliSock = tcpCliSock

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        device = torch.device('cpu')
        net = ConvFCNet().to(device)
        model = torch.load('models/cnn_model.pkl',map_location=torch.device('cpu'))
        if isinstance(model, torch.nn.DataParallel):
            net = model.module
        net.eval()
        # net.load_state_dict(torch.load('cnn_model.pkl', map_location=torch.device('cpu')))
        protobufhello = self.tcpCliSock.recv(BUFSIZ)
        hello_message = message.Hello()
        hello_message.ParseFromString(protobufhello)
        print(hello_message)
        # seat = hello_message.seat
        # print('seat', seat)
        print("Hello")
        hello_message.code = 2
        self.tcpCliSock.send(hello_message.SerializeToString())
        while True:
            # Head_data = tcpCliSock.recv(4)  # 接收数据头 4个字节,
            # data_len = int.from_bytes(Head_data, byteorder='big')
            # print("入座成功")
            print("is recving")
            protobufdata = self.tcpCliSock.recv(BUFSIZ)
            print("recv")
            game_state_message = message.GameState()  # 读取GameState
            game_state_message.ParseFromString(protobufdata)
            # print('id:', tableid)
            # print(game_state_message)
            player = game_state_message.who
            feature = GameState2feature_cnn(game_state_message)
            # print(len(feature))
            card_logits = net(torch.tensor(feature).float()[None,:])
            resort_card_logits = torch.zeros_like(card_logits[0])
            resort_card_logits[:13] = card_logits[0,-13:]
            resort_card_logits[13:26] = card_logits[0,-26:-13]
            resort_card_logits[26:39] = card_logits[0,13:26]
            resort_card_logits[-13:] = card_logits[0,0:13]
            # 加一层mask
            validPlays = game_state_message.validPlays
            # print(seat,validPlays)
            output_mask = [0] * 52
            for card in validPlays:
                # print(card)
                output_mask[card.suit * 13 + card.rank] = 1
            # print(output_mask)
            # print(card_logits.data)
            masked_logits = torch.nn.functional.softmax(resort_card_logits, 0).data * torch.tensor(output_mask) + torch.tensor(output_mask)
            pred = masked_logits.max(0)[1]
            card = message.Card()
            card.suit = int(int(pred) / 13)
            card.rank = int(pred) % 13
            play = message.Play()
            play.who = player
            play.card.CopyFrom(card)
            self.tcpCliSock.send(play.SerializeToString())
            print("play")


thread_num = 1
thread_list = []
tcpCliSock = []
for i in range(thread_num):
    tcpCliSocki = socket(AF_INET, SOCK_STREAM)
    tcpCliSocki.connect(ADDR)
    thread_list.append(clientThread(i + 1, "Thread-" + str(i), i + 1, tcpCliSocki))
    tcpCliSock.append(tcpCliSocki)
    thread_list[i].start()

