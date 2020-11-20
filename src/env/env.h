#pragma once

#include <iostream>
#include <sstream>
#include <string.h>
#include <vector>
#include <map>
#include <algorithm>
#include <random>
#include <chrono>
#include <./Card.h>
#include <./Player.h>
#include <./Contract.h>
#include <./Round.h>
using namespace std;
using std::ostream;
using std::istream;
using std::stringstream;
using std::endl;
using std::string;
using std::vector;

class env {
 private:
 public:
    Contract contract;
    vector<Round> playHistory;
    vector<Player> players;
    Player whooseTurn;
    map<Player, vector<Card>> handCards;
    void init(bool bid=false, bool sample=false);

    env(){ }

    void init(bool bid=false, bool sample=false){
        if(bid){
            // run bid process
        }
        else if(sample){
            // sample from dataset
        }
        else{
            contract = Contract(NOTRUMP, 3);
            vector<Player> tmp = contract.getPlayers();
            players = tmp;
            // for(auto i=0; i<tmp.size(); i++){
            //     handCards[tmp[i]] = vector
            // }
            int tmpCard[52];
            for(int i=0;i<52;i++){
                tmpCard[i] = i;
            }
            unsigned seed = std::chrono::system_clock::now ().time_since_epoch ().count ();  
            shuffle(begin(tmpCard), end(tmpCard), std::default_random_engine (seed));
            for(auto i=0; i<tmp.size();i++){
                for(auto j=0; j<13; j++){
                    auto cardEncode = tmpCard[13*i+j];
                    handCards[tmp[i]].push_back(Card(cardEncode/13, cardEncode%13));
                }
            }
            whooseTurn = tmp[1];
            cout << "using random cards" << endl;
            print();
        }
    }

    void print(){
        cout << contract << endl;
        for(auto i=0; i < playHistory.size(); i++){
            cout << playHistory[i] << endl;
        }
        for(auto i=0; i<players.size(); i++){
            cout << players[i] << "\n\t";
            for(auto j=0; j<handCards[players[i]].size(); j++){
                cout << handCards[players[i]][j] << " ";
            }
            cout << endl;
        }
        cout << "whoose turn: " << whooseTurn << endl;
    }
};
