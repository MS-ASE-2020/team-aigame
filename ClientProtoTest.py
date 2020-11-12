from socket import *
import google.protobuf
import protobuf.message_pb2 as message
import traceback
import google.protobuf.any_pb2
# from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from demo import *
import threading

HOST = '192.168.0.100'
PORT = 11087
BUFSIZ = 1024
ADDR = (HOST, PORT)


class clientThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        tcpCliSock = socket(AF_INET, SOCK_STREAM)
        tcpCliSock.connect(ADDR)
        seat = 5
        while True:
            # Head_data = tcpCliSock.recv(4)  # 接收数据头 4个字节,
            # data_len = int.from_bytes(Head_data, byteorder='big')
            # 等待Hello
            while seat == 5:
                protobufhello = tcpCliSock.recv(BUFSIZ)
                hello_message = message.Hello()
                hello_message.ParseFromString(protobufhello)
                seat = 5 if hello_message is None else hello_message.seat

            protobufdata = tcpCliSock.recv(BUFSIZ)

            game_state_message = message.GameState()  # 读取GameState
            game_state_message.ParseFromString(protobufdata)
            tableid = game_state_message.tableID
            print('id:', tableid)
            player = game_state_message.who
            assert player == seat
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
            tcpCliSock.send(card.SerializeToString())

# tcpCliSock.close()
thread_num = 4
thread_list = []
for i in range(thread_num):
    thread_list.append(clientThread(i+1, "Thread-"+str(i), i+1))
    thread_list[i].start()

