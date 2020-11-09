#include "engine.h"
#include "stringify.h"
#include "dummyPlayer.h"
#include <algorithm>
#include <random>
#include <cassert>

BridgeGame::BridgeGame(){
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> dist(0, 3);
    int tmp = dist(gen);
    switch(tmp){
        case 0:
        vulnerability = Vul::NONE;
        break;
        case 1:
        vulnerability = Vul::CONTRACT;
        break;
        case 2:
        vulnerability = Vul::DEFENDER;
        break;
        case 3:
        vulnerability = Vul::BOTH;
        break;
        default:
        vulnerability = Vul::NONE;
        break;
    }

    init();
}

BridgeGame::BridgeGame(Vul vul): vulnerability(vul){
    init();
}

void BridgeGame::init(){
    restart();

    for(auto pPlayer: players){
        pPlayer = nullptr;
    }

    // Set to 3NT
    contract.set_doubled(Contract_Doubled::Contract_Doubled_NO);
    contract.set_level(3);
    contract.set_suit(Suit::NT);

    currentTrick = 0;
    currentCardInTrick = 0;
}

void BridgeGame::restart(){
    Deck drawDeck;
    drawDeck.initFullDeck();
    drawDeck.shuffle();

    Player players[] = {Player::DECLARER, Player::LOPP, Player::DUMMY, Player::ROPP};
    while(!drawDeck.isEmpty()){
        for(auto player : players){
            hands[player].append(drawDeck.draw());
        }
    }
}

void BridgeGame::sit(IPlayer *p, Player seat){
    players[seat] = p;
    p->setHand(&hands[seat]);
}

GameResult BridgeGame::run(){
    GameResult ret;

    for(auto pPlayer: players){
        if(pPlayer == nullptr || !pPlayer->isReady()){
            throw 1;
        }
    }

    Player currentPlayer;
    for(int trick = 0; trick < 13; ++trick){
        currentPlayer = findLead(trick);
        for(int player = 0; player < 4; ++player){
            fprintf(stdout, "Playing card %d of trick %d\n", player, trick);
            int trick_save = currentTrick;
            int card_save = currentCardInTrick;

            if(currentPlayer == Player::DUMMY){
                IPlayer *declarer = players[Player::DECLARER];
                declarer->setHand(&hands[Player::DUMMY]);
                declarer->playAs(this, Player::DUMMY);
                declarer->setHand(&hands[Player::DECLARER]);
            }
            else{
                players[currentPlayer]->play(this);
            }
            
            // Ensure 1 card is played
            assert((currentCardInTrick == card_save + 1 && currentTrick == trick_save)
                || (currentCardInTrick == 0 && currentTrick == trick_save + 1));

            currentPlayer = findNextK(currentPlayer, 1);
        }
    }

    return ret;
}

Player BridgeGame::findLead(int trick){
    if(trick == 0){
        return Player::LOPP;
    }
    else{
        return trickWinner[trick - 1];
    }
}

Player BridgeGame::findNextK(Player base, int offset){
    static const Player answer[][4] = {
        {Player::DECLARER, Player::LOPP, Player::DUMMY, Player::ROPP},  // Base: DECLARER
        {Player::LOPP, Player::DUMMY, Player::ROPP, Player::DECLARER},  // Base: LOPP
        {Player::DUMMY, Player::ROPP, Player::DECLARER, Player::LOPP},  // Base: DUMMY
        {Player::ROPP, Player::DECLARER, Player::LOPP, Player::DUMMY},  // Base: ROPP
        };
    return answer[base][offset];
}

Player BridgeGame::findTrickWinner(int trick){
    Suit trump = contract.suit();
    auto beatsPrevWinner = [&trump](Card prevWinner, Card card){
        if(card.suit() != prevWinner.suit()){
            if(card.suit() == trump){
                return true;
            }
            else{
                return false;
            }
        }
        else{
            if(card.rank() == 1){
                return true;
            }
            else if(prevWinner.rank() == 1){
                return false;
            }
            else{
                return card.rank() > prevWinner.rank();
            }
        }
    };

    Card winner = getHistory(trick, 0);
    int winnerIndex = 0;
    for(int i = 1; i < 4; ++i){
        Card card = getHistory(trick, i);
        if(beatsPrevWinner(winner, card)){
            winner = card;
            winnerIndex = i;
        }
    }

    StringConverter* global = StringConverter::getInstance();
    printf("Winner of trick %d: %s%s\n", trick+1, global->convert(winner.suit()), global->convert(winner.rank()));

    return findNextK(findLead(trick), winnerIndex);
}

void BridgeGame::switchSide(){
    Deck temp;
    temp = hands[Player::DECLARER];
    hands[Player::DECLARER] = hands[Player::LOPP];
    hands[Player::LOPP] = hands[Player::DUMMY];
    hands[Player::DUMMY] = hands[Player::ROPP];
    hands[Player::ROPP] = temp;
}

void BridgeGame::playCard(Player who, Card what){
    hands[who].remove(what);
    history[currentTrick][currentCardInTrick] = what;

    ++currentCardInTrick;
    if(currentCardInTrick == 4){
        trickWinner[currentTrick] = findTrickWinner(currentTrick);
        currentCardInTrick = 0;
        ++currentTrick;
    }
}

void BridgeGame::dumpState(FILE *fout){
    fprintf(fout, "===== Begin table info =====\n\n");
    fprintf(fout, "=== Card holdings ===\n");
    char const * seats[] = {"N", "E", "S", "W"};
    Player players[] = {Player::DUMMY, Player::ROPP, Player::DECLARER, Player::LOPP};
    Suit suits[] = {Suit::S, Suit::H, Suit::D, Suit::C};

    StringConverter * global = StringConverter::getInstance();

    for(int i = 0; i < 4; ++i){
        fprintf(fout, seats[i]);
        for(auto suit: suits){
            fprintf(fout, "\t%s ", global->convert(suit));
            std::vector<Card> suitcard = hands[i].filter([suit](Card c){
                return c.suit() == suit;
            });
            if(suitcard.empty()){
                fprintf(fout, "-\n");
            }
            else{
                std::sort(suitcard.begin(), suitcard.end(), [](const Card& card1, const Card& card2){
                    if(card1.rank() == 1){
                        return true;
                    }
                    else if(card2.rank() == 1){
                        return false;
                    }

                    return card1.rank() > card2.rank();
                });
                for(auto card: suitcard){
                    fprintf(fout, "%s", global->convert(card.rank()));
                }
                fprintf(fout, "\n");
            }
        }
        fprintf(fout, "\n");
    }
}