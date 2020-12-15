import socket
import google.protobuf
import google.protobuf.any_pb2
import protobuf.message_pb2 as message
from demo import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HostPort = ('192.168.0.100', 11087)
s.bind(HostPort)  # 绑定地址端口
s.listen(5)  # 监听最多5个连接请求
while True:
    print('server socket waiting...')
    obj, addr = s.accept()  # 阻塞等待链接
    print('socket object:', obj)
    print('client info:', addr)
    while True:
        Head_data = obj.recv(4)  # 接收数据头 4个字节,
        data_len = int.from_bytes(Head_data, byteorder='big')

        protobufdata = obj.recv(data_len)

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
        obj.send(card)


