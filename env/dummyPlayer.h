#pragma once

#include "IPlayer.h"

class DummyPlayer final: public IPlayer{
    private:
    public:
    DummyPlayer(): IPlayer(Player::DUMMY){}
    ~DummyPlayer(){}

    bool isReady() override {
        return true;
    }

    void play(BridgeGame *pEngine) override {}
};