#pragma once

#include "IPlayer.h"

class LocalPlayer final : public IPlayer {
    public:
    LocalPlayer(Player p): IPlayer(p){}
    ~LocalPlayer(){}

    bool isReady() override;
    void play(BridgeGame *pEngine) override;
};