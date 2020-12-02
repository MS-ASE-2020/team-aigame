import gym
import torch 
import torch.nn as nn
from torch import optim 
import numpy as np 
import numpy.ma as ma 
import sys

from contract_bridge.envs.bridge_trick_taking import BridgeEnv
from networks.nn import DQN
from networks.buffers import ReplayMemory, Transition
from agents.agent import SmartGreedyAgent, RandomAgent

import click
import random
import os

def train(n_episodes, is_random, epsilon=0.1):
    env = gym.make('contract_bridge:contract-bridge-v0')

    batch_size = 128
    gamma = 0.999
    target_update = 1000 # update target network after 1000 episodes
    steps_done = 0

    device = torch.device('cpu')
    policy_dqn = DQN().to(device)
    target_dqn = DQN().to(device)
    target_dqn.load_state_dict(policy_dqn.state_dict())

    optimizer = optim.Adam(policy_dqn.parameters(), lr=0.0001)
    criterion = nn.SmoothL1Loss()
    replay_memory = ReplayMemory(100000)

    #DQN is p_00, p_01 is a teammate, the rest are opponents
    players = {}
    players['p_01'] = RandomAgent('p_01', env) if is_random else SmartGreedyAgent('p_01', env)
    players['p_10'] = RandomAgent('p_10', env) if is_random else SmartGreedyAgent('p_10', env)
    players['p_11'] = RandomAgent('p_11', env) if is_random else SmartGreedyAgent('p_11', env)

    #to determine ordering
    order = ['p_00', 'p_11', 'p_01', 'p_10']
    sliding_window = []

    for episode in range(n_episodes):

        #reset the environment with a new random bid
        bid_level = random.randint(7,13)
        bid_trump = random.choice(['C', 'D', 'H', 'S', None])
        bid_trump = None
        bid_team = random.choice([0,1])
        env.reset(bid_level, bid_trump, bid_team)

        for r in range(13):

            prev_dqn_state = None
            dqn_action = None

            for i in range(4):
                #the environment tells us which player should go next
                pid = env.current_player

                if pid == 'p_00':
                    #dqn agent
                    prev_dqn_state = env.get_state('p_00').to(device)

                    #Epsilon-greedy action selection
                    if random.random() < epsilon:

                        #pick a random card (exploration)
                        card = random.choice(env.hands['p_00'])
                        dqn_action = torch.LongTensor([env.card_to_index[card]])
                        env.play({'player': 'p_00', 'card': card})
                    
                    else:
                        #get the dqn output
                        output = policy_dqn.forward(prev_dqn_state)
                        hand = env.hands['p_00']

                        card_index = None
                        for card in hand:
                            temp_index = env.card_to_index[card]
                            if card_index is None or output[temp_index] > output[card_index]:
                                card_index = temp_index

                        dqn_action = torch.LongTensor([card_index])
                        #chosen card at the index
                        card = env.index_to_card[card_index]
                        env.play({'player': 'p_00', 'card': card})
                
                else:
                    card = players[pid].act()
                    env.play({'player': pid, 'card': card})
            
            env.step('p_01')
            (_, op_reward, _, _)  = env.step('p_10')
            env.step('p_11')
            (obs, reward, done, info) = env.step('p_00')

            if len(sliding_window) == 100:
                sliding_window.pop(0)
                sliding_window.append(1 if reward > op_reward else 0)
            else:
                sliding_window.append(1 if reward > op_reward else 0)
            
            if r == 12 and episode % 1000 == 0 and len(sliding_window) == 100:
                with open('logs/%s.txt' % ('sliding-random' if is_random else 'sliding-smart'), 'a+') as f:
                    f.write('%d %f\n' % (episode, sum(sliding_window)/len(sliding_window)))
            
            reward_tensor = torch.tensor([reward], device=device)
            next_dqn_state = env.get_state('p_00')
            replay_memory.push(prev_dqn_state.unsqueeze(dim = 0), dqn_action, 
                reward_tensor.unsqueeze(dim = 0), next_dqn_state.unsqueeze(dim = 0))

            if len(replay_memory) > batch_size:
                #get transitions of size "batch_size"
                transitions = replay_memory.sample(batch_size)
                batch = Transition(*zip(*transitions))
                mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), 
                    device=device, dtype=torch.bool)
                
                next_states = torch.cat([s for s in batch.next_state if s is not None]).to(device)
                state_batch = torch.cat(batch.state)
                next_state_batch = torch.cat(batch.next_state)
                action_batch = torch.cat(batch.action)
                reward_batch = torch.cat(batch.reward).squeeze(1)
                
                q_values = policy_dqn(state_batch.to(device))
                q_values = q_values.gather(-1, action_batch.unsqueeze(dim = 1))
                
                next_state_values = torch.zeros(batch_size, device=device)
                next_out = target_dqn(next_states)
                next_state_values[mask] = next_out.max(1)[0].detach()
                expected_q_values = ((next_state_values * gamma) + reward_batch.float())

                #compute loss
                loss = criterion(q_values.squeeze(1), expected_q_values)

                optimizer.zero_grad()
                loss.backward()
                for param in policy_dqn.parameters():
                    param.grad.data.clamp_(-1, 1)
                
                optimizer.step()
                
        
        # update the target network based on the current policy
        # also save the current policy network
        if episode % target_update == 0:
            target_dqn.load_state_dict(policy_dqn.state_dict())
        
        if episode % 10000 == 0:
            torch.save(policy_dqn.state_dict(), "models/%s/policy-network-%d.pth" % ('random' if is_random else 'smart', episode))

    env.close()


if __name__ == '__main__':

    #make sure directories exist to save models and performance logs
    if not os.path.exists("models"):
        os.mkdir("models")
    
    if not os.path.exists("logs"):
        os.mkdir("logs")
    
    is_random = sys.argv[1] == 'random'
    
    if not os.path.exists('models/%s' % ('random' if is_random else 'smart')):
        os.mkdir('models/%s' % ('random' if is_random else 'smart'))
    
    train(100000, is_random)
    print('done')
