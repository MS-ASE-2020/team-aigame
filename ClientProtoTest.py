from socket import *
import google.protobuf

import protobuf.message_pb2 as message
import traceback
import google.protobuf.any_pb2
# from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from demo import *
import threading

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

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        # tcpCliSock = socket(AF_INET, SOCK_STREAM)
        # tcpCliSock.connect(ADDR)
        # 等待Hello
        # protobufhello = self.tcpCliSock.recv(BUFSIZ)
        # hello_message = message.GameState()
        # hello_message.ParseFromString(protobufhello)
        # print(hello_message)
        # seat = hello_message.seat
        # print('seat',seat)
        print("Hello")
        while True:
            # Head_data = tcpCliSock.recv(4)  # 接收数据头 4个字节,
            # data_len = int.from_bytes(Head_data, byteorder='big')
            # print("入座成功")
            print("is recving")
            protobufdata = self.tcpCliSock.recv(BUFSIZ)
            print("recv")
            game_state_message = message.GameState()  # 读取GameState
            game_state_message.ParseFromString(protobufdata)
            tableid = game_state_message.tableID
            print('id:', tableid)
            print('message:',game_state_message)
            player = game_state_message.who
            # assert player == seat
            if player == 0:
                # Declare
                card = declarer(game_state_message, "easy")
                # 发送
            elif player == 1:
                card = lopp(game_state_message, "easy")
            elif player == 2:
                card = dummy(game_state_message, "easy")
            else:
                card = ropp(game_state_message, "easy")
            play = message.Play()
            play.tableID = tableid
            play.who = player
            play.card.CopyFrom(card)
            self.tcpCliSock.send(play.SerializeToString())
            print("play")

# tcpCliSock.close()
thread_num = 3
thread_list = []
tcpCliSock = []
for i in range(thread_num):
    tcpCliSocki = socket(AF_INET, SOCK_STREAM)
    tcpCliSocki.connect(ADDR)
    thread_list.append(clientThread(i+1, "Thread-"+str(i), i+1, tcpCliSocki))
    tcpCliSock.append(tcpCliSocki)
    thread_list[i].start()

