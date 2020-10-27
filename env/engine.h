#pragma once

#include "message.pb.h"
#include "deck.h"

class BridgeGame final {
    private:
    Deck hands[Player::NUM_PLAYERS];
    public:
    BridgeGame();
    ~BridgeGame(){}

    void restart();
    GameResult run();
};