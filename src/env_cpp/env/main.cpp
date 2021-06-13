#include <cstdio>
#include "engine.h"
#include "message.pb.h"
#include "localPlayer.h"
#include "dummyPlayer.h"
#include "networkManager.h"

int main(int argc, char *argv[]){
    if(argc < 2){
        return 1;
    }

    short port = atoi(argv[1]);

    NetworkManager mgr(port);
    int connectedPlayer = 0;

    size_t capacity = 4096;
    char *buffer = new char[capacity];
    while(connectedPlayer < 4){
        NetworkManager::Connection conn = mgr.waitForConnection();
        size_t msglen = 0;
        int ret = mgr.recv(conn, buffer, capacity, msglen);
        if(ret > 0){
            capacity = ret;
            delete[] buffer;
            buffer = new char[capacity];
            ret = mgr.recv(conn, buffer, capacity, msglen);
            if(ret != 0){
                printf("NetworkManager::recv() fails\n");
                throw 1;
            }
        }

        Hello msgHello;
        msgHello.ParseFromArray(buffer + sizeof(uint32_t), msglen - sizeof(uint32_t));
        
        printf("Hello for table %u\n", msgHello.code());
    }

    delete[] buffer;

    BridgeGame game;
    IPlayer *player[4];
    player[Player::DUMMY] = new DummyPlayer;
    player[Player::DECLARER] = new LocalPlayer(Player::DECLARER);
    player[Player::LOPP] = new LocalPlayer(Player::LOPP);
    player[Player::ROPP] = new LocalPlayer(Player::ROPP);

    for(int i = 0; i < 4; ++i){
        game.sit(player[i], (Player)i);
    }

    game.dumpState(stdout);
    game.run();
    game.dumpState(stdout);
    return 0;
}