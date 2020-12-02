from itertools import product
import numpy as np
from torch import Tensor
import random

import gym
from gym import spaces, utils
from gym.error import InvalidAction
from .deck import Card, Deck

class BridgeEnv(gym.Env):
    """
    This environment doesn't exactly fit the OpenAI Gym API
    """
    def __init__(self):
        pass

    def initialize(self, bid_level, bid_trump, bid_team, game_case):
        """
        bid_level - number of tricks ( > 6) that bidder bets on taking
        bid_trump - the trump suit of this round's bid
        bid_maker - which side made the bid (either 0 or 1)
        game_case - a game data from dataset
        """
        self.bid_level = bid_level
        self.bid_trump = bid_trump
        self.bid_team = bid_team
        self.game_case = game_case
        self.player_list = ['p_00', 'p_11', 'p_01', 'p_10']
        self.round_index = -1
        self.win_count = [0,0]
        self.identity = self.game_case['identity']

        self.open_player = [k for k, v in self.identity.items() if v == [0, 1, 0]][0]
        self.banker_player = [k for k, v in self.identity.items() if v == [1, 0, 0]][0]


        #calculate the index of the current bid
        self.bid_index = ['C','D','H','S', None].index(bid_trump)*7 + (bid_level-7)

        #create a list of cards in sorted order (an index -> card map)
        self.index_to_card = sorted([Card(rank=x[0], suit=x[1], trump=bid_trump) 
                for x in product(Card.ranks, Card.suits)])

        #create a dictionary mapping cards to index
        self.card_to_index = {}
        for index,card in enumerate(self.index_to_card):
            self.card_to_index[card] = index

        #now initialize relevant variables for starting state (beginning of round)
        self.trick_history = []
        self.current_trick = []
        self.trick_winner = None
        self.round_over = False

        #determine the starting player
        # self.current_player = 'p_%d%d' % (bid_team, 1 if random.random() < 0.5 else 0)

        self.current_player = self.game_case['starting_player']

        #keep track of each team's score
        self.team0_num_tricks = 0
        self.team1_num_tricks = 0
        self.team0_score = None
        self.team1_score = None

        #some variables to keep track of the state representation given to neural networks
        self.played_cards = {'p_00': [], 'p_01': [], 'p_10': [], 'p_11': []}
        self.played_cards_vector = ({'p_00': np.zeros((52,)), 'p_01': np.zeros((52,)),
            'p_10': np.zeros((52,)), 'p_11': np.zeros((52,))})

        self.played_this_trick = {'p_00': None, 'p_01': None, 'p_10': None, 'p_11': None}
        self.hands = {'p_00': [], 'p_01': [], 'p_10': [], 'p_11': []}
        self.hands_vector = ({'p_00': np.zeros((52,)), 'p_01': np.zeros((52,)),
            'p_10': np.zeros((52,)), 'p_11': np.zeros((52,))})

        self._deal()
    

    def reset(self, bid_level, bid_trump, bid_team, game_case):
        self.initialize(bid_level, bid_trump, bid_team, game_case)

    def _deal(self):
        index = 0
        players = ['p_00', 'p_01', 'p_10', 'p_11']
        self.hands = {'p_00': [], 'p_01': [], 'p_10': [], 'p_11': []}

        self.deck = Deck(trump=self.bid_trump)

        # 在这里把生成的牌，按照牌例分给四位选手

        # while not self.deck.is_empty():
        #     card = self.deck.deal()
        #     self.hands[players[index]].append(card)
        #     self.hands_vector[players[index]][self.card_to_index[card]] = 1
        #     index = (index+1) % 4

        while not self.deck.is_empty():
            _ = self.deck.deal()

        for k, v in self.game_case['player_cards'].items():
            for card in v:
                self.hands[k].append(self.index_to_card[card])
                self.hands_vector[k][card] = 1


    def _calculate_score(self, team):
        """
        Calculate the score achieved by the input team (0 or 1)
        Output: integer score
        """
        score = 0
        n_tricks = self.team0_num_tricks if team == 0 else self.team1_num_tricks

        if self.bid_team == team:
            if self.bid_trump is None:
                return 0 if n_tricks == 0 else 10 + n_tricks*30
            else:
                return n_tricks*(30 if self.bid_trump in ('H', 'S') else 20)
        else:
            return 50*max(0, self.bid_level-n_tricks)

    def get_state(self, player):
        """
        Return the tensor representation of the state visible to each player
        This computation is broken up into stages and then concatenated at the end
        """
        teammate = self.get_teammate(player)
        left = self.get_left_opponent(player)
        right = self.get_right_opponent(player)

        #round_index_vector
        round_index_vector = [0] * 13
        round_index_vector[self.round_index] = 1

        #bid_vector
        bid_vector = [0] * 12
        bid_vector[int(self.bid_level)-6] = 1
        if self.bid_trump == None:
            bid_vector[11] = 1
        else:
            bid_vector[['S', 'H', 'D', 'C'].index(self.bid_trump) + 7] = 1

        win_count = self.win_count

        #get identity
        identity_vector = self.identity[player]

        #get current hand
        current_hand_vector = self.hands_vector[player]

        #get open_hand
        if player != self.open_player:
            open_hand_vector =  self.hands_vector[self.open_player]
        else:
            open_hand_vector = self.hands_vector[self.banker_player]


        #teammate, left, right opponent play history
        self_hsitory_vector = self.played_cards_vector[player]
        teammate_history_vector = self.played_cards_vector[teammate]
        left_history_vector = self.played_cards_vector[left]
        right_history_vector = self.played_cards_vector[right]

        #teammate, left, right opponent plays this trick
        teammate_current_trick = np.zeros((52,))
        left_current_trick = np.zeros((52,))
        right_current_trick = np.zeros((52,))

        if self.played_this_trick[teammate] is not None:
            card = self.played_this_trick[teammate]
            teammate_current_trick[self.card_to_index[card]] = 1

        if self.played_this_trick[left] is not None:
            card = self.played_this_trick[left]
            left_current_trick[self.card_to_index[card]] = 1

        if self.played_this_trick[right] is not None:
            card = self.played_this_trick[right]
            right_current_trick[self.card_to_index[card]] = 1

        #the bid that was made for this round
        #bid = np.zeros((35,))
        #bid[self.bid_index] = 1

        #whether this team or the opponent made the bid
        #index 0 is this team, 1 is the opponent
        #team = int(player[2])
        #bid_team = np.array([1,0] if self.bid_team==team else [0,1])

        #concatenate into 1 numpy array and convert into a PyTorch tensor
        concat_tuple = ((round_index_vector, bid_vector, win_count, identity_vector, current_hand_vector, open_hand_vector,
                         self_hsitory_vector, teammate_history_vector, left_history_vector,right_history_vector,
                         teammate_current_trick, left_current_trick,right_current_trick))
        
        return Tensor(np.concatenate(concat_tuple))

    def get_teammate(self, player):
        players = ['p_00', 'p_11', 'p_01', 'p_10']
        index = players.index(player)
        return players[(index+2) % len(players)]

    def get_left_opponent(self, player):
        players = ['p_00', 'p_11', 'p_01', 'p_10']
        index = players.index(player)
        return players[(index-1) % len(players)]

    def get_right_opponent(self, player):
        players = ['p_00', 'p_11', 'p_01', 'p_10']
        index = players.index(player)
        return players[(index+1) % len(players)]

    def play(self, action):
        """
        Action must be an object with the following attributes:
            - player = 'p_00', 'p_01', 'p_10', or 'p_11'
            - card = some card object, must be in player's hand at that point

        Updates the apprpriate player's hand as well as trick history
        All 4 agents call this method before "step" to get the appropriate reward
        """
        player = action['player']
        card = action['card']

        #make sure the player is the one who should be playing this turn
        if player != self.current_player:
            raise Exception("Player %s should play this turn, not player %s" % 
                (self.current_player, player))
        
        self.current_trick.append((player, card))

        #remove the played card from appropriate player's hand and set it
        #as their played card this trick
        player_hand = self.hands[player]
        self.played_this_trick[player] = player_hand.pop(player_hand.index(card))
        self.hands_vector[player][self.card_to_index[card]] = 0

        #the trick is over
        if len(self.current_trick) == 4:
            current_trick_sorted = sorted(self.current_trick, key=lambda x: x[1], reverse=True)
            # 如果是无将，需要进一步处理排序后的结果（考虑第一手牌的花色）
            if self.current_trick[0][1].trump is None:
                for i in range(len(current_trick_sorted)):
                    if current_trick_sorted[i][1].suit == self.current_trick[0][1].suit:
                        current_trick_sorted[0], current_trick_sorted[i] = current_trick_sorted[i], current_trick_sorted[0]
                        break

            #calculate the winner and add it to the history
            self.trick_winner = int(current_trick_sorted[0][0][2])
            self.trick_history.append(self.current_trick)

            if self.trick_winner == 0:
                self.team0_num_tricks += 1
                self.win_count[0] += 1
            else:
                self.team1_num_tricks += 1
                self.win_count[1] += 1

            #now add each player's card to their respective histories
            for p in self.played_this_trick:
                self.played_cards[p].append(self.played_this_trick[p])
                self.played_cards_vector[p][self.card_to_index[self.played_this_trick[p]]] = 1
                self.played_this_trick[p] = None
            
            #the next player is the one who won this trick
            self.current_player = current_trick_sorted[0][0]

            #clear the cards for current trick
            self.current_trick = []

        else:
            #if the trick isn't over, the next player is the next player in the list (mod 4, of course)
            index = self.player_list.index(self.current_player)
            self.current_player = self.player_list[(index+1) % 4]

        #if the round is over, calculate scores for each team based on the bid
        if len(self.trick_history) == 13:
            self.round_over = True
            self.team0_score = 20 if self.team0_num_tricks > self.team1_num_tricks else -20 
            self.team1_score = 20 if self.team1_num_tricks > self.team0_num_tricks else -20

    def step(self, player):
        """
        player - one of 'p_00', 'p_01', 'p_10', or 'p_11'
        """
        if self.round_over:
            return (None, self.team0_score if int(player[2])==0 else self.team1_score, True, None)
        else:
            return (None, 1 if int(player[2])==self.trick_winner else -1, False, None)