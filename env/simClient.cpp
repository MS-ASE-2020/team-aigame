#include <cstdio>

#include "networkManager.h"

int main(){
    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(10086);
    inet_aton("10.0.0.5", &(addr.sin_addr));

    Client(addr);
    return 0;
}