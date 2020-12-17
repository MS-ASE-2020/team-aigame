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
#include <./env.h>
using namespace std;
using std::ostream;
using std::istream;
using std::stringstream;
using std::endl;
using std::string;
using std::vector;

int main(){
    env Env = env();
    Env.init();
    return 0;
}
