#pragma once

#ifndef __linux__
#error OS not supported
#endif

#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#include <cstdio>

class NetworkManager final{
    private:
    int m_listen;

    static int send_internal(int socket, void *data, size_t datalen){
        size_t sent = 0;
        while(sent < datalen){
            ssize_t ret = ::send(socket, data, datalen, 0);
            if(ret <= 0){
                printf("::send() fails\n");
                throw 1;
            }

            sent += ret;
        }

        return 0;
    }

    public:
    using Connection = int;

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

        if(listen(m_listen, 5) == -1){
            printf("listen() failed on port %hu.\n", port);
            throw 1;
        }
    }

    Connection waitForConnection(){
        return accept(m_listen, nullptr, nullptr);
    }

    ~NetworkManager(){
        close(m_listen);
    }

    static int send(int socket, char* data, size_t datalen, size_t &sent){
        sent = 0;
        uint32_t len = static_cast<uint32_t>(datalen);
        uint32_t lenConverted = htonl(len);
        NetworkManager::send_internal(socket, &lenConverted, sizeof(lenConverted));
        NetworkManager::send_internal(socket, data, datalen);

        sent = datalen + sizeof(lenConverted);
        return 0;
    }

    static int recv(int socket, char *data, size_t capacity, size_t &copied){
        copied = 0;
        uint32_t sizebuf;
        ssize_t ret = ::recv(socket, &sizebuf, sizeof(uint32_t), MSG_PEEK);
        if(ret != sizeof(uint32_t)){
            printf("::recv() fails\n");
            throw 1;
        }

        uint32_t size = ntohl(sizebuf);
        size_t totalSize = size + sizeof(size);
        size_t read = 0;
        if(totalSize > capacity){
            return static_cast<int>(totalSize);
        }

        while(read < totalSize){
            ret = ::recv(socket, data + read, totalSize - read, 0);
            if(ret <= 0){
                printf("::recv() fails\n");
                throw 1;
            }

            read += ret;
        }

        copied = read;

        return 0;
    }
};

class Client final{
    private:
    int m_socket;
    public:
    Client(struct sockaddr_in remoteAddr){
        m_socket = socket(AF_INET, SOCK_STREAM, 0);
        connect(m_socket, (sockaddr *)&remoteAddr, sizeof(remoteAddr));
    }

    ~Client(){
        close(m_socket);
    }
};