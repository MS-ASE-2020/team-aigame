from socket import *
import google.protobuf
import protobuf.message_pb2 as message
import traceback
import google.protobuf.any_pb2
# from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from demo import *

HOST = '192.168.0.100'
PORT = 11087
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpCliSock = socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)

while True:
    Head_data = tcpCliSock.recv(4)  # 接收数据头 4个字节,
    data_len = int.from_bytes(Head_data, byteorder='big')

    protobufdata = tcpCliSock.recv(data_len)

    game_state_message = message.GameState()  # 读取GameState
    game_state_message.ParseFromString(protobufdata)
    tableid = game_state_message.tableID
    print('id:', tableid)
    player = game_state_message.who
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
    tcpCliSock.send(card)

tcpCliSock.close()
