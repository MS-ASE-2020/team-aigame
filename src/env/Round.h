#pragma once

#include <iostream>
#include <sstream>
#include <string.h>
#include <assert.h>
#include <Card.h>
#include <Player.h>
using std::ostream;
using std::istream;
using std::stringstream;
using std::endl;
using std::string;

struct Round {
 public:
    Card card[4];
    Player lead;
    bool finished=false;
    Player winner;
    Round() {
        lead = new Player();
    }

};