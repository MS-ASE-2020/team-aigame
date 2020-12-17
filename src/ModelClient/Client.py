"""
Integrate All Models to One Client
"""

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
from Model import MLP,DQN,ConvFCNet
from FeatureGeneration import GameState2feature_cnn,GameState2feature_DQN,GameState2feature_MLP
from RuleBased import *


HOST = '127.0.0.1'
PORT = 6006
BUFSIZ = 1024
ADDR = (HOST, PORT)


class clientThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID, name, counter, tcpCliSock):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.tcpCliSock = tcpCliSock
        self.model_map = {1:"Rule_based", 2:"DQN_SL",3:"DQN_RL"}

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        if self.model_map[self.threadID] == "Rule_based":
            # 等待Hello
            protobufhello = self.tcpCliSock.recv(BUFSIZ)
            hello_message = message.Hello()
            hello_message.ParseFromString(protobufhello)
            print(hello_message)
            print("Hello")
            hello_message.code = 1 # Rule_based
            self.tcpCliSock.send(hello_message.SerializeToString())
            while True:
                print("is recving")
                protobufdata = self.tcpCliSock.recv(BUFSIZ)
                print("recv")
                game_state_message = message.GameState()  # 读取GameState
                game_state_message.ParseFromString(protobufdata)
                player = game_state_message.who
                if player == 0:
                    # Declare
                    card = declarer(game_state_message, "hard")
                    # 发送
                elif player == 1:
                    card = lopp(game_state_message, "hard")
                elif player == 2:
                    card = dummy(game_state_message, "hard")
                else:
                    card = ropp(game_state_message, "hard")
                play = message.Play()
                play.who = player
                play.card.CopyFrom(card)
                self.tcpCliSock.send(play.SerializeToString())
                print("play")
        elif self.model_map[self.threadID] == "DQN_SL":
            device = torch.device('cpu')
            net = DQN().to(device)
            net.eval()
            net.load_state_dict(torch.load('models/trained_agents/bridge_agent_14-16_v5.pth', map_location=torch.device('cpu')))
            protobufhello = self.tcpCliSock.recv(BUFSIZ)
            hello_message = message.Hello()
            hello_message.ParseFromString(protobufhello)
            print(hello_message)
            print("Hello")
            hello_message.code = 2
            self.tcpCliSock.send(hello_message.SerializeToString())
            while True:
                print("is recving")
                protobufdata = self.tcpCliSock.recv(BUFSIZ)
                print("recv")
                game_state_message = message.GameState()  # 读取GameState
                game_state_message.ParseFromString(protobufdata)
                player = game_state_message.who
                feature = GameState2feature_DQN(game_state_message)
                card_logits = net(torch.tensor(feature).float())
                # 加一层mask
                validPlays = game_state_message.validPlays
                output_mask = [0] * 52
                for card in validPlays:
                    output_mask[card.suit * 13 + card.rank] = 1
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
        elif self.model_map[self.threadID] == "DQN_RL":
            device = torch.device('cpu')
            net = [DQN().to(device) for i in range(4)]
            map_dirname = {0:'declarer',1:'lopp',2:'dummy',3:'ropp'}
            for i in range(4):
                net[i].eval()
                net[i].load_state_dict(torch.load('models/DQN/'+map_dirname[i]+'/policy-network-30000.pth', map_location=torch.device('cpu')))
            protobufhello = self.tcpCliSock.recv(BUFSIZ)
            hello_message = message.Hello()
            hello_message.ParseFromString(protobufhello)
            print(hello_message)
            print("Hello")
            hello_message.code = 3
            self.tcpCliSock.send(hello_message.SerializeToString())
            while True:
                print("is recving")
                protobufdata = self.tcpCliSock.recv(BUFSIZ)
                print("recv")
                game_state_message = message.GameState()  # 读取GameState
                game_state_message.ParseFromString(protobufdata)
                player = game_state_message.who
                feature = GameState2feature_DQN(game_state_message)
                card_logits = net[player](torch.tensor(feature).float())
                # 加一层mask
                validPlays = game_state_message.validPlays
                output_mask = [0] * 52
                for card in validPlays:
                    output_mask[card.suit * 13 + card.rank] = 1
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
        elif self.model_map[self.threadID] == "MLP":
            device = torch.device('cpu')
            net = MLP().to(device)
            net.load_state_dict(torch.load('models/SL_V1.pth', map_location=torch.device('cpu')))
            protobufhello = self.tcpCliSock.recv(BUFSIZ)
            hello_message = message.Hello()
            hello_message.ParseFromString(protobufhello)
            print(hello_message)
            print("Hello")
            hello_message.code = 2
            self.tcpCliSock.send(hello_message.SerializeToString())
            while True:
                print("is recving")
                protobufdata = self.tcpCliSock.recv(BUFSIZ)
                print("recv")
                game_state_message = message.GameState()  # 读取GameState
                game_state_message.ParseFromString(protobufdata)
                player = game_state_message.who
                feature = GameState2feature_MLP(game_state_message)
                card_logits = net(torch.tensor(feature).float())
                # 加一层mask
                validPlays = game_state_message.validPlays
                output_mask = [0] * 52
                for card in validPlays:
                    output_mask[card.suit * 13 + card.rank] = 1
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
        elif self.model_map[self.threadID] == "CNN_SL":
            device = torch.device('cpu')
            net = ConvFCNet().to(device)
            model = torch.load('models/cnn_model.pkl',map_location=torch.device('cpu'))
            if isinstance(model, torch.nn.DataParallel):
                net = model.module
            net.eval()
            protobufhello = self.tcpCliSock.recv(BUFSIZ)
            hello_message = message.Hello()
            hello_message.ParseFromString(protobufhello)
            print(hello_message)
            print("Hello")
            hello_message.code = 2
            self.tcpCliSock.send(hello_message.SerializeToString())
            while True:
                print("is recving")
                protobufdata = self.tcpCliSock.recv(BUFSIZ)
                print("recv")
                game_state_message = message.GameState()  # 读取GameState
                game_state_message.ParseFromString(protobufdata)
                player = game_state_message.who
                feature = GameState2feature_cnn(game_state_message)
                card_logits = net(torch.tensor(feature).float()[None,:])
                resort_card_logits = torch.zeros_like(card_logits[0])
                resort_card_logits[:13] = card_logits[0,-13:]
                resort_card_logits[13:26] = card_logits[0,-26:-13]
                resort_card_logits[26:39] = card_logits[0,13:26]
                resort_card_logits[-13:] = card_logits[0,0:13]
                # 加一层mask
                validPlays = game_state_message.validPlays
                output_mask = [0] * 52
                for card in validPlays:
                    output_mask[card.suit * 13 + card.rank] = 1
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


thread_num = 3
thread_list = []
tcpCliSock = []
for i in range(thread_num):
    tcpCliSocki = socket(AF_INET, SOCK_STREAM)
    tcpCliSocki.connect(ADDR)
    thread_list.append(clientThread(i + 1, "Thread-" + str(i), i + 1, tcpCliSocki))
    tcpCliSock.append(tcpCliSocki)
    thread_list[i].start()

