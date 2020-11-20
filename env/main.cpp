#include <cstdio>
#include "engine.h"
#include "message.pb.h"
#include "localPlayer.h"
#include "dummyPlayer.h"
#include "networkManager.h"

int main(){
    NetworkManager mgr(10086);
    int connectedPlayer = 0;

    while(connectedPlayer < 4){
        NetworkManager::Connection conn = mgr.waitForConnection();
        
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