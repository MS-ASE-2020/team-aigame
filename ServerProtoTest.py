import socket
import google.protobuf
import google.protobuf.any_pb2
import protobuf.message_pb2

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

        tmessage = TransportMessage_pb2.TransportMessage()
        tmessage.ParseFromString(protobufdata)
        i_id = tmessage.Id
        i_msgtype = tmessage.MsgType
        print('id:', i_id, 'msgType:', i_msgtype)
        if i_msgtype == 0:
            print('异常')
            break
        if i_msgtype == 1010:
            print('服务器接收到心跳包...')
        if i_msgtype == 1020:
            print('服务器接收到上线通知...')
            online = WeChatOnlineNoticeMessage_pb2.WeChatOnlineNoticeMessage()
            tmessage.Content.Unpack(online)
            print('WeChatNo:' + online.WeChatNo, 'WeChatId:' + online.WeChatId, 'WeChatNick:' + online.WeChatNick)