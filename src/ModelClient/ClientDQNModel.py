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
import protobuf.protobuf_modify.message1_pb2 as message
from protobuf.protobuf_modify.message1_pb2 import GameState, TrickHistory
from socket import *
import threading
import os

HOST = '127.0.0.1'
PORT = 6006
BUFSIZ = 1024
ADDR = (HOST, PORT)

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
    history_cards = [[0]*52 for i in range(4)]
    teammate_history_cards = [0]*52
    left_history_cards = [0]*52
    right_history_cards = [0]*52
    self_history_cards = [0]*52
    round_cards = [[0]*52 for i in range(4)]
    teammate_current_trick = [0]*52
    left_current_trick = [0]*52
    right_current_trick = [0]*52
    if len(playHistorys) == 0:
        pass
    else:
        for index, history in enumerate(playHistorys):
            # dun count
            if index != 0 and (history.lead == who or history.lead == (who+2) % 4):
                dun_count_feature[who % 2] += 1
            elif index != 0:
                dun_count_feature[(who+1) % 2] += 1
            else:
                pass

            # history cards
            who_round = history.lead
            # desktop_cards_feature
            for card in history.cards:
                desktop_cards_feature[card.suit * 13 + card.rank] = 1
                if index == len(playHistorys) - 1:
                    round_cards[who_round % 4][card.suit * 13 + card.rank] = 1
                history_cards[who_round % 4][card.suit * 13 + card.rank] = 1
                who_round += 1

            # round_out_cards
            if index == len(playHistorys) - 1:
                for card in history.cards:
                    round_out_cards_feature[card.suit * 13 + card.rank] = 1
        teammate_current_trick = round_cards[(2+who) % 4]
        left_current_trick = round_cards[(1+who) % 4]
        right_current_trick = round_cards[(3+who) % 4]
        teammate_history_cards = history_cards[(2+who) % 4]
        left_history_cards = history_cards[(1+who) % 4]
        right_history_cards = history_cards[(3+who) % 4]
        self_history_cards = history_cards[who]

    for card in game_state.hand:
        hand_card_feature[card.suit * 13 + card.rank] = 1

    for card in game_state.dummy:
        open_hand_feature[card.suit * 13 + card.rank] = 1
    # print(teammate_current_trick,teammate_history_cards)
    sum_card_feature = np.asarray(hand_card_feature) + np.asarray(open_hand_feature) + np.asarray(desktop_cards_feature)
    remaining_cards_feature = list(np.asarray([1]*52) - sum_card_feature)
    cat_feature = round_index_feature + bidding_feature + dun_count_feature + identity + hand_card_feature + open_hand_feature + self_history_cards + teammate_history_cards + left_history_cards + right_history_cards + teammate_current_trick + left_current_trick + right_current_trick
    return cat_feature


class clientThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID, name, counter, tcpCliSock):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.tcpCliSock = tcpCliSock
        self.model_dir = 'models/DQN/'

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        device = torch.device('cpu')
        net = [DQN().to(device) for i in range(4)]
        map_dirname = {0:'declarer',1:'lopp',2:'dummy',3:'ropp'}
        for i in range(4):
            net[i].eval()
            net[i].load_state_dict(torch.load(self.model_dir+map_dirname[i]+'/policy-network-30000.pth', map_location=torch.device('cpu')))
        protobufhello = self.tcpCliSock.recv(BUFSIZ)
        hello_message = message.Hello()
        hello_message.ParseFromString(protobufhello)
        print(hello_message)
        # seat = hello_message.seat
        # print('seat', seat)
        print("Hello")
        hello_message.code = 3
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
            feature = GameState2feature(game_state_message)
            # print(len(feature))
            card_logits = net[player](torch.tensor(feature).float())
            # 加一层mask
            validPlays = game_state_message.validPlays
            # print(seat,validPlays)
            output_mask = [0] * 52
            for card in validPlays:
                # print(card)
                output_mask[card.suit * 13 + card.rank] = 1
            # print(output_mask)
            # print(card_logits.data)
            masked_logits = card_logits.data * torch.tensor(output_mask) + torch.tensor(output_mask)
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

