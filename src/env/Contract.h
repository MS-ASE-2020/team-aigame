#pragma once

#include <iostream>
#include <sstream>
#include <string.h>
#include <./Card.h>
#include <./Player.h>
#include <vector>
using std::ostream;
using std::istream;
using std::stringstream;
using std::endl;
using std::string;
using std::vector;

enum Doubled {
    NODOUBLE = 0,
    X = 1,
    XX = 2,
};

class Contract {
 public:
    vector<Card> history;
    Doubled doubled = NODOUBLE;
    Suit suit;
    int level;
    Contract(){ }
    Contract(int x, int y) {
        suit = (Suit)x;
        level = y;
    }
    Contract(Suit x, int y){
        suit = x;
        level = y;
    }
    void add(Suit x, int y){
        // bid, to be implement
    }
    vector<Player> getPlayers(){
        vector<Player> tmp;
        if(history.size()==0){
            for(auto i=0; i<4; i++){
                tmp.push_back(Player(i, i));
            }
        }
        else{
            // assign roles according to bid history
            assert(history.size()>=4);
            for(auto i=0;i<4;i++){
                tmp.push_back(Player(i, (history.size()+i)%4));
            }
        }
        return tmp;
    }

    friend ostream& operator<< (ostream& os, const Contract& c) {
        os << "contract suit: " << c.suit << endl;
        os << "         level: " << c.level << endl;
        os << "         double: " << c.doubled << endl;
        // print history if necessary
        return os;
    }
};
