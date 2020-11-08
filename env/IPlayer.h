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

    void setHand(Deck *d){
        pHand = d;
    }
};