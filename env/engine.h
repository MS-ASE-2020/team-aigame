#pragma once

#include "message.pb.h"
#include "deck.h"
#include <cstdio>
#include "IPlayer.h"

class BridgeGame final {
    private:
    Deck hands[Player::NUM_PLAYERS];
    Vul vulnerability;
    std::vector<std::vector<Card>> history;

    IPlayer *players[Player::NUM_PLAYERS];
    Contract contract;

    void init();
    public:
    BridgeGame();
    BridgeGame(Vul vul);
    ~BridgeGame(){}

    void restart();
    void switchSide();
    void sit(IPlayer *p, Player seat);
    GameResult run();

    std::vector<std::vector<Card>>* getPtrHistory(){
        return &history;
    }

    Vul getVulnerability(){
        return vulnerability;
    }

    void playCard(Player who, Card what);

    void setContract(Contract c){
        contract = c;
    }

    Contract getContract(){
        return contract;
    }

    Suit getTrumpSuit(){
        return contract.suit();
    }

    bool isLeadingNewTrick();
    Player getNextPlayer(Player prev);

    void dumpState(FILE *fout);
};