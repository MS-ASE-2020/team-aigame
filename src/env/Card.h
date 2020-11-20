#pragma once

#include <iostream>
#include <sstream>
#include <string.h>
#include <assert.h>
using std::ostream;
using std::istream;
using std::stringstream;
using std::endl;
using std::string;

enum Suit {
    CLUB = 0,
    C = 0,
    DIAMOND = 1,
    D = 1,
    HEART = 2,
    H = 2,
    SPADE = 3,
    S = 3,
    NOTRUMP = 4,
    NT = 4,
    DOUBLE = 5,
    X = 5,
    PASS = 6,
    P = 6,
    UNDEFINED = 7
};

class Card {
    public:
    Suit suit = UNDEFINED;
    int rank = -1;
    Card() { }
    Card(int x, int y) {
        assert(y>=0 && y<=12);
        assert(x>=0 && x<=6);
        suit = (Suit)x;
        rank = y;
    }
    Card(Suit x, int y) {
        assert(y>=0 && y<=12);
        suit = x;
        rank = y;
    }
    bool operator==(const Card& x) const {
        return rank == x.rank && suit == x.suit;
    }

    bool operator!=(const Card& x) const {
        return !(*this == x);
    }

    friend ostream& operator<< (ostream& os, const Card& x) {
        string t;
        switch(x.suit){
            case CLUB: t = "CLUB"; break;
            case DIAMOND: t = "DIAMOND"; break;
            case HEART: t = "HEART"; break;
            case SPADE: t = "SPADE"; break;
            default: t = "other suit"; break;
        }
        os << t << "," << x.rank;
        return os;
    }
};
