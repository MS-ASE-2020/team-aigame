#pragma once

#include "message.pb.h"
#include <deque>
#include <vector>
#include <functional>

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

    int size(){
        return cards.size();
    }

    void remove(Card card){
        for(auto it = cards.begin(); it != cards.end(); ++it){
            if(it->suit() == card.suit() && it->rank() == card.rank()){
                cards.erase(it);
                return;
            }
        }

        throw 2;
    }
    
    void shuffle();

    std::vector<Card> filter(std::function<bool(Card)> func);
};
