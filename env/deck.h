#pragma once

#include "message.pb.h"
#include <deque>

class Deck final {
    friend class BridgeGame;

    private:
    std::deque<Card> cards;
    void initFullDeck();

    public:
    Deck(): cards(){}
    ~Deck(){}

    Card draw(){
        Card ret = cards.front();
        cards.pop_front();
        return ret;
    }

    void append(Card card){
        cards.push_back(card);
    }

    bool isEmpty(){
        return cards.empty();
    }
    
    void shuffle();
};
