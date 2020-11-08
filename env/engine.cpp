#include "engine.h"
#include "stringify.h"
#include <algorithm>
#include <random>

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

    Player order[] = {Player::DECLARER, Player::LOPP, Player::DUMMY, Player::ROPP, Player::DECLARER};

    for(int trick = 0; trick < 13; ++trick){
        for(int player = 0; player < 4; ++player){
            fprintf(stdout, "Playing card %d of trick %d\n", player, trick);
            players[player]->play(this);
        }
    }

    return ret;
}

bool BridgeGame::isLeadingNewTrick(){
    return history.empty() || history[history.size() - 1].size() == 4;
}

Player BridgeGame::getNextPlayer(Player prev){
    if(!isLeadingNewTrick()){
        switch(prev){
            case Player::LOPP:
            return Player::DUMMY;
            case Player::DUMMY:
            return Player::ROPP;
            case Player::ROPP:
            return Player::DECLARER;
            case Player::DECLARER:
            return Player::LOPP;
        }
    }
    else{
        // TODO
        return Player::DECLARER;
    }
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
    if(isLeadingNewTrick()){
        std::vector<Card> newTrick;
        newTrick.emplace_back(what);
        history.emplace_back(newTrick);
    }
    else{
        history[history.size() - 1].emplace_back(what);
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