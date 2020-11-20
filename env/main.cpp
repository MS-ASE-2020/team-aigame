#include <cstdio>
#include "engine.h"
#include "message.pb.h"
#include "localPlayer.h"
#include "dummyPlayer.h"
#include "networkManager.h"
#include "scaleArray.hpp"

int main(){
    NetworkManager mgr(10086);
    int connectedPlayer = 0;

    AlgoLib::DataStructure::ScaleArray<char> buffer(4096);
    while(connectedPlayer < 4){
        NetworkManager::Connection conn = mgr.waitForConnection();
        size_t msglen = 0;
        int ret = mgr.recv(conn, buffer.data(), buffer.capacity(), msglen);
        if(ret > 0){
            buffer.reserve(ret);
            ret = mgr.recv(conn, buffer.data(), buffer.capacity(), msglen);
            if(ret != 0){
                printf("NetworkManager::recv() fails\n");
                throw 1;
            }
        }

        Hello msgHello;
        msgHello.ParseFromArray(buffer.data() + sizeof(uint32_t), msglen - sizeof(uint32_t));
        
        printf("Hello for table %u\n", msgHello.code());
    }


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