#include "localPlayer.h"
#include "engine.h"
#include "stringify.h"
#include <random>

bool LocalPlayer::isReady(){
    return true;
}

void LocalPlayer::play(BridgeGame *pEngine){
    std::vector<Card> choices;
    if(pEngine->getCurrentCardInTrick() == 0){
        // Lead new trick
        if(pEngine->getCurrentTrick() >= 13){
            throw 1;
        }

        choices = &(pHand->filter([](Card c){
            return true;
        }));
    }
    else{
        // Follow
        Card lead = pEngine->getHistory(pEngine->getCurrentTrick(), 0);
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