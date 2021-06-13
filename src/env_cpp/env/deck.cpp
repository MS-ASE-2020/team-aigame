#include "deck.h"
#include <algorithm>
#include <random>

void Deck::initFullDeck(){
    Suit suits[] = {Suit::S, Suit::H, Suit::D, Suit::C};
    for(auto suit : suits){
        for(int rank = 1; rank <= 13; ++rank){
            Card card;
            card.set_suit(suit);
            card.set_rank(rank);
            cards.push_back(card);
        }
    }
}

void Deck::shuffle(){
    std::random_device rd;
    std::mt19937 gen(rd());

    std::shuffle(cards.begin(), cards.end(), gen);
}

std::vector<Card> Deck::filter(std::function<bool(Card)> func){
    std::vector<Card> ret;
    for(auto const& card: cards){
        if(func(card)){
            ret.push_back(Card(card));
        }
    }

    return ret;
}