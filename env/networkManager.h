#pragma once

#ifndef __linux__
#error OS not supported
#endif

#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#include <cstdio>

class NetworkManager{
    private:
    int m_listen;
    public:
    NetworkManager(unsigned short port){
        m_listen = socket(AF_INET, SOCK_STREAM, 0);
        if(m_listen == -1){
            printf("socket() failed.\n");
            throw 1;
        }

        sockaddr_in addrListen;
        addrListen.sin_family = AF_INET;
        addrListen.sin_port = htons(port);
        addrListen.sin_addr.s_addr = INADDR_ANY;

        if(bind(m_listen, (struct sockaddr *)&addrListen, sizeof(addrListen)) == -1){
            printf("bind() failed on port %hu.\n", port);
            throw 1;
        }
    }

    ~NetworkManager(){
        close(m_listen);
    }
};