#include <cstdio>

#include "networkManager.h"
#include "message.pb.h"

int main(int argc, char* argv[]){
    if(argc < 2){
        return 1;
    }

    int selection = atoi(argv[1]);

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(10086);
    inet_aton("10.0.0.5", &(addr.sin_addr));

    Client client(addr);

    Hello hello;
    hello.set_code(4788);
    hello.set_seat(static_cast<Player>(selection));
    hello.set_isobserver(false);

    std::string buffer;
    hello.SerializeToString(&buffer);
    size_t sent = 0;
    client.send(buffer.c_str(), buffer.size(), sent);
    return 0;
}