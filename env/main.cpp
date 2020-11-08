#include <cstdio>
#include "engine.h"
#include "message.pb.h"
#include "localPlayer.h"

int main(){
    BridgeGame game;
    LocalPlayer *player[4];
    player[0] = new LocalPlayer(Player::DECLARER);
    player[1] = new LocalPlayer(Player::LOPP);
    player[2] = new LocalPlayer(Player::DUMMY);
    player[3] = new LocalPlayer(Player::ROPP);
    for(int i = 0; i < 4; ++i){
        game.sit(player[i], (Player)i);
    }

    game.dumpState(stdout);
    game.run();
    game.dumpState(stdout);
    return 0;
}