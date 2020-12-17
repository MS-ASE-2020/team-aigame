import random
from functools import total_ordering
from itertools import product
import torch

@total_ordering
class Card:
    #12-14 is J, Q, K, A
    ranks = (2,3,4,5,6,7,8,9,10,11,12,13,14)
    suits = ('C','D','H','S')
    suit_orders = {'C': ['D', 'H', 'S', 'C'], 'D': ['C', 'H', 'S', 'D'], 
    'H': ['C', 'D', 'S', 'H'], 'S': ['C', 'D', 'H', 'S'], None: ['C', 'D', 'H', 'S']}
    
    def __init__(self, rank, suit, trump=None):
        if rank in Card.ranks:
            self.rank = rank
        else:
            raise Exception('The rank must be an integer between 2 and 14 inclusive.')

        if suit in Card.suits:
            self.suit = suit
        else:
            raise Exception('The suit must be \'C\', \'D\', \'H\', or \'S\'.')

        #used when determining card precedence during each round
        self.trump = trump
    
    def to_tensor(self):
        index = Card.suit_orders[self.trump].index(self.suit)*13 + (self.rank-2)
        tensor = torch.zeros(52)
        tensor[index] = 1
        return tensor.long()
    
    def __str__(self):
        if (self.rank == 14):
            rank = 'A'
        elif (self.rank == 13):
            rank = 'K'
        elif (self.rank == 12):
            rank = 'Q'
        elif (self.rank == 11):
            rank = 'J'
        else:
            rank = str (self.rank)
        return rank + self.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))
    
    def __eq__ (self, other):
        return (self.trump == other.trump) and (self.rank == other.rank) and (self.suit == other.suit)
    
    def __ne__ (self, other):
        return not self.__eq__(other)
    
    def _no_trump_compare(self, other):
        if self.suit != other.suit:
            return self.suit < other.suit
        else:
            return self.rank < other.rank
    
    def __lt__ (self, other):
        #you can only compare cards with the same trump suit
        if self.trump != other.trump:
            raise Exception('You can only compare cards with the same trump suit.')

        #if there is no trump suit or either both or neither cards are 
        #trump defer to a regular comparison
        if self.trump is None or ((self.suit == self.trump) == (other.suit == self.trump)):
            return self._no_trump_compare(other)
        else:
            #precisely one of the cards is trump
            return self.suit != self.trump

class Deck:

    def __init__(self, trump=None):
        self.trump = trump
        self.deck = list(map(lambda x: Card(rank=x[0], suit=x[1], trump=trump), 
                        product(Card.ranks, Card.suits)))

        # 因为按牌例发牌，所以注释掉了
        # self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.deck)
    
    def is_empty(self):
        return len(self.deck) == 0
    
    def deal(self):
        if self.is_empty():
            return None
        else:
            return self.deck.pop(0)
    
    def __str__(self):
        return ', '.join(map(lambda x: str(x), self.deck))