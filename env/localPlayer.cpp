#include "localPlayer.h"
#include "engine.h"
#include "stringify.h"
#include <random>

bool LocalPlayer::isReady(){
    return true;
}

void LocalPlayer::play(BridgeGame *pEngine){
    auto pHistory = pEngine->getPtrHistory();
    std::vector<Card> &choices = std::vector<Card>();
    if(pHistory->empty() || pHistory->at(pHistory->size() - 1).size() == 4){
        // Lead new trick
        if(pHistory->size() >= 13){
            throw 1;
        }

        choices = pHand->filter([](Card c){
            return true;
        });
    }
    else{
        // Follow
        Card lead = pHistory->at(pHistory->size() - 1)[0];
        choices = pHand->filter([&lead](Card c){
            return c.suit() == lead.suit();
        });

        if(choices.empty()){
            choices = pHand->filter([&lead](Card c){
                return true;
            });
        }
    }

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> dist(0, choices.size() - 1);
    
    Card chosen = choices[dist(gen)];
    StringConverter *global = StringConverter::getInstance();
    printf("Play card %s%s\n", global->convert(chosen.suit()), global->convert(chosen.rank()));
    pEngine->playCard(identity, chosen);
}