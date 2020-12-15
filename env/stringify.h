#pragma once

#include <string>
#include <map>
#include "message.pb.h"

class StringConverter{
    private:
    typedef uint32_t Rank;

    StringConverter(): mapSuit(), mapRank(){}
    static StringConverter *instance;

    std::map<Suit, const char *> mapSuit;
    std::map<Rank, const char *> mapRank;

    public:
    static StringConverter *getInstance(){
        if(instance == nullptr){
            instance = new StringConverter();

            instance->mapSuit.insert(std::make_pair(Suit::S, "S"));
            instance->mapSuit.insert(std::make_pair(Suit::H, "H"));
            instance->mapSuit.insert(std::make_pair(Suit::D, "D"));
            instance->mapSuit.insert(std::make_pair(Suit::C, "C"));

            instance->mapRank.insert(std::make_pair(1, "A"));
            instance->mapRank.insert(std::make_pair(2, "2"));
            instance->mapRank.insert(std::make_pair(3, "3"));
            instance->mapRank.insert(std::make_pair(4, "4"));
            instance->mapRank.insert(std::make_pair(5, "5"));
            instance->mapRank.insert(std::make_pair(6, "6"));
            instance->mapRank.insert(std::make_pair(7, "7"));
            instance->mapRank.insert(std::make_pair(8, "8"));
            instance->mapRank.insert(std::make_pair(9, "9"));
            instance->mapRank.insert(std::make_pair(10, "T"));
            instance->mapRank.insert(std::make_pair(11, "J"));
            instance->mapRank.insert(std::make_pair(12, "Q"));
            instance->mapRank.insert(std::make_pair(13, "K"));
        }

        return instance;
    }

    const char * convert(Suit suit){
        return mapSuit[suit];
    }

    const char * convert(Rank rank){
        return mapRank[rank];
    }

};