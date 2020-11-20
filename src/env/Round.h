#pragma once

#include <iostream>
#include <sstream>
#include <string.h>
#include <assert.h>
#include <vector>
#include <./Card.h>
#include <./Player.h>
using std::ostream;
using std::istream;
using std::stringstream;
using std::endl;
using std::string;
using std::vector;

class Round {
 public:
    vector<Card> card;
    Player lead;
    Suit leadSuit;
    Player winner;
    Player expectedNextPlayer;

    Round(){
        lead = Player();
        winner = Player();
        leadSuit = UNDEFINED;
        expectedNextPlayer = Player();
    }

    // check if this round is finished
    bool is_finshed(){
        if(count==4){
            winner = getWinner();
            return true;
        }
        else
        {
            return false;
        }
    }

    void add(Card c, Player p){
        if(card.size()==0){
            lead = p;
            leadSuit = c.suit;
            assert(p.role!=NOROLE);
            expectedNextPlayer.role = (Role)((p.role+1)%4);
            card.push_back(c);
        }
        else{
            assert(p.role==expectedNextPlayer.role);
            card.push_back(c);
        }
        count++;
    }

    friend ostream& operator<< (ostream& os, const Round& r) {
        os << "lead: " << r.lead << ", " 
           << "lead suit: " << r.leadSuit << ", "
           << "winner: " << r.winner << "\n";
        for(auto i=0; i<r.card.size(); i++){
            os << r.card[i];
        }
        os << "\nexpected next player: " << r.expectedNextPlayer;
        return os;
    }
 private:
    int count = 0;
    Player getWinner(){
        assert(card.size()<=4);
        if(card.size()<4)
            return Player();
        auto maxPlayer = 0;
        for(auto i=1 ; i < card.size(); i++){
            if(card[i].suit==leadSuit && card[i].rank > card[maxPlayer].rank){
                maxPlayer = i;
            }
        }
        return Player((lead.role+maxPlayer)%4, (lead.direction+maxPlayer)%4);
    }
};
