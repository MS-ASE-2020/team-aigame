#include "engine.h"

BridgeGame::BridgeGame(){
    restart();
}

void BridgeGame::restart(){
    Deck drawDeck;
    drawDeck.initFullDeck();
    drawDeck.shuffle();

    Player players[] = {Player::DECLARER, Player::LOPP, Player::DUMMY, Player::ROPP};
    while(!drawDeck.isEmpty()){
        for(auto player : players){
            hands[player].append(drawDeck.draw());
        }
    }
}

GameResult BridgeGame::run(){
    GameResult ret;
    return ret;
}