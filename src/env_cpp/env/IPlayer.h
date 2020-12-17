#pragma once

#include "deck.h"
#include "message.pb.h"

class BridgeGame;

class IPlayer{
    protected:
    Deck *pHand;
    Player identity;

    public:
    IPlayer(Player p): identity(p){}
    virtual ~IPlayer(){}

    virtual bool isReady() = 0;
    virtual void play(BridgeGame *pEngine) = 0;
    virtual void playAs(BridgeGame *pEngine, Player id){
        Player id_save = identity;
        identity = id;
        play(pEngine);
        identity = id_save;
    }

    void setHand(Deck *d){
        pHand = d;
    }
};