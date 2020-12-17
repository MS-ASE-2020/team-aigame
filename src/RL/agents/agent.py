import argparse
import sys
import math
import random
import numpy as np
import torch 
from torch import nn, optim

from networks.nn import DQN
from networks.buffers import ReplayMemory, Transition
from contract_bridge.envs.bridge_trick_taking import BridgeEnv

class Agent(object):
    """
    Base class for agents interacting with the Bridge environment
    """
    def __init__(self, pid, env):
        self.pid = pid
        self.env = env
    
    def act(self):
        raise NotImplementedError()

class SmartGreedyAgent(Agent):
    def __init__(self, pid, env):
        super().__init__(pid, env)
    
    def act(self):
        hand = self.env.hands[self.pid]
        highest_played = None

        if len(self.env.current_trick) > 0:
            highest_played = sorted(list(map(lambda x: x[1], self.env.current_trick)))[-1]
        else:
            #first player in this trick, so just play the highest card
            return sorted(hand)[-1]
        
        #ids of other players
        teammate = self.env.get_teammate(self.pid)
        left_op = self.env.get_left_opponent(self.pid)
        right_op = self.env.get_right_opponent(self.pid)
        
        #cards that others have played
        played_this_trick = self.env.played_this_trick
        teammate_card = played_this_trick[teammate]
        left_op_card = played_this_trick[left_op]
        right_op_card = played_this_trick[right_op]
        
        if teammate_card is not None:
            if left_op_card is not None and right_op_card is not None:
                if teammate_card > max(left_op_card, right_op_card):
                    #if teammate already won the trick, just burn the worst card
                    return min(hand)
        
        return self._play_worst_winning(hand, left_op_card, right_op_card)

    def _get_highest_op_card(self, left_op_card, right_op_card):
        #when this function is called, we know at least 1 opponent has played a card
        if left_op_card is not None and right_op_card is not None:
            return max(left_op_card, right_op_card)
        elif left_op_card is not None:
            return left_op_card
        else:
            return right_op_card
    
    def _play_worst_winning(self, hand, left_op_card, right_op_card):
        #play the smallest winning card, if none exists burn the worst card
        highest_op_card = self._get_highest_op_card(left_op_card, right_op_card)
        hand_sorted = sorted(hand)

        for card in hand_sorted:
            if card > highest_op_card:
                #card is the smallest card that can win
                return card
        
        #can't win, so might as well burn the lowest card
        return hand_sorted[0]

class RandomAgent(Agent):
    def __init__(self, pid, env):
        super().__init__(pid, env)
    
    def act(self):
        return random.choice(self.env.hands[self.pid])

class DQNAgent(Agent):
    def __init__(self, pid, env, mode='train', policy_dqn=None, epsilon=0.1, buffer_size=100000):
        super().__init__(pid, env)

        self.mode = mode

        #networks determine agent's behavior
        self.device = torch.device('cpu')

        if type(policy_dqn) == str:
            self.policy_dqn = DQN().to(self.device)
            self.policy_dqn.load_state_dict(torch.load(policy_dqn, map_location='cpu'))
        else:
            self.policy_dqn = policy_dqn.to(self.device) if policy_dqn is not None else DQN().to(self.device)
        
        self.target_dqn = DQN().to(self.device)
        self.target_dqn.load_state_dict(self.policy_dqn.state_dict())
        self.epsilon = epsilon
        
        #training variables
        self.criterion = nn.SmoothL1Loss()
        self.optimizer = optim.Adam(self.policy_dqn.parameters(), lr=0.0001)
        self.gamma = 0.999
        self.prev_state = None
        self.action = None
        self.batch_size = 128
        self.last_loss = None

        #used for experience replay
        self.buffer_size = buffer_size
        self.replay_memory = ReplayMemory(buffer_size)
    
    def act(self):
        #dqn agent
        self.prev_state = self.env.get_state(self.pid).to(self.device)

        #Epsilon-greedy action selection
        if self.mode == 'train' and random.random() < self.epsilon:

            #pick a random card (exploration)
            card = random.choice(self.env.hands[self.pid])
            self.action = torch.LongTensor([self.env.card_to_index[card]])
            return card
        
        else:
            #get the dqn output
            output = self.policy_dqn.forward(self.prev_state)
            hand = self.env.hands[self.pid]

            #pick highest value card in the player's hand
            card_index = None
            for card in hand:
                temp_index = self.env.card_to_index[card]
                if card_index is None or output[temp_index] > output[card_index]:
                    card_index = temp_index
            
            self.action = torch.LongTensor([card_index])
            
            #chosen card at the index
            card = self.env.index_to_card[card_index]
            return card
    
    def process_step(self, reward):

        reward_tensor = torch.tensor([reward], device=self.device)
        next_dqn_state = self.env.get_state(self.pid)
        self.replay_memory.push(self.prev_state.unsqueeze(dim = 0), self.action, 
            reward_tensor.unsqueeze(dim = 0), next_dqn_state.unsqueeze(dim = 0))
        
        if len(self.replay_memory) >= self.batch_size:
            #get transitions of size "batch_size"
            transitions = self.replay_memory.sample(self.batch_size)
            batch = Transition(*zip(*transitions))
            mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), 
                device=self.device, dtype=torch.bool)

            next_states = torch.cat([s for s in batch.next_state if s is not None]).to(self.device)
            state_batch = torch.cat(batch.state)
            next_state_batch = torch.cat(batch.next_state)
            action_batch = torch.cat(batch.action)
            reward_batch = torch.cat(batch.reward).squeeze(1)
            
            q_values = self.policy_dqn(state_batch.to(self.device))
            q_values = nn.functional.softmax(q_values, dim = 1)
            q_values = q_values.gather(- 1, action_batch.unsqueeze(dim = 1))
            
            next_state_values = torch.zeros(self.batch_size, device=self.device)
            next_out = self.target_dqn(next_states)
            next_state_values[mask] = next_out.max(1)[0].detach()
            expected_q_values = (next_state_values * self.gamma) + reward_batch.float()

            #compute loss
            loss = self.criterion(q_values.squeeze(1), expected_q_values)
            self.optimizer.zero_grad()
            loss.backward()

            for param in self.policy_dqn.parameters():
                param.grad.data.clamp_(-1, 1)
            
            self.optimizer.step()
            self.last_loss = loss.item()
    
    def target_update(self):
        #update target to match the policy
        self.target_dqn.load_state_dict(self.policy_dqn.state_dict())

