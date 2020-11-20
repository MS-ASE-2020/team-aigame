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

enum Role {
    DECLARER = 0,
    LOPP = 1,
    DUMMY = 2,
    ROPP = 3,
    NO = 4
};

enum Direction {
    NORTH = 0,
    EAST = 1,
    SOUTH = 2,
    WEST = 3,
    NO = 4
};

struct Player {
    Role role;
    Direction direction;
    Player() { 
        role = (Role)4;
        direction = (Direction)4;
    }
    Player(int x, int y) {
        assert(y>=0 && y<=4);
        assert(x>=0 && x<=4);
        role = (Role)x;
        direction = (Direction)y;
    }
    Player(Role x, int y) {
        assert(y>=0 && y<=4);
        role = x;
        direction = (Direction)y;
    }
    Player(int x, Direction y) {
        assert(x>=0 && y<=4);
        role = (Role)x;
        direction = y;
    }
    Player(Role x, Direction y) {
        role = x;
        direction = y;
    }

    bool operator==(const Player& x) const {
        return role == x.role && direction == x.direction;
    }

    bool operator!=(const Player& x) const {
        return !(*this == x);
    }

};