#pragma once

#include "message.pb.h"
#include "deck.h"
#include <cstdio>
#include "IPlayer.h"

class BridgeGame final {
    private:
    Deck hands[Player::NUM_PLAYERS];
    Vul vulnerability;
    Card history[13][4];
    Player trickWinner[13];
    int currentTrick;
    int currentCardInTrick;

    IPlayer *players[Player::NUM_PLAYERS];
    Contract contract;

    void init();

    Player findLead(int trick);
    Player findTrickWinner(int trick);
    Player findNextK(Player base, int offset);
    public:
    BridgeGame();
    BridgeGame(Vul vul);
    ~BridgeGame(){}

    void restart();
    void switchSide();
    void sit(IPlayer *p, Player seat);
    GameResult run();

    Card getHistory(int trick, int cardInTrick){
        return history[trick][cardInTrick];
    }

    Vul getVulnerability(){
        return vulnerability;
    }

    int getCurrentTrick(){
        return currentTrick;
    }

    int getCurrentCardInTrick(){
        return currentCardInTrick;
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

    void dumpState(FILE *fout);
};