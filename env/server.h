#pragma once

#include "message.pb.h"

// for dev
#define __linux__
#ifdef __linux__

#include <errno.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>


class ProtobufServer{
    private:
    int m_sockListen;
    public:
    ProtobufServer(short port){
        m_sockListen = socket(AF_INET, SOCK_STREAM, 0);
        if(m_sockListen == -1){
            throw errno;
        }

        struct sockaddr_in bindingAddr;
        bindingAddr.sin_family = AF_INET;
        bindingAddr.sin_port = htons(port);
        bindingAddr.sin_addr.s_addr = INADDR_ALL;
    }
    ~ProtobufServer(){}

};

#else
#error OS not supported
#endif