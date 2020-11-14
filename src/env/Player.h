#pragma once

#include <iostream>
#include <sstream>
#include <string.h>
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
    WEST = 3
};