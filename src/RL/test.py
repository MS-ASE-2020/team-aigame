import gym
import torch 
import torch.nn as nn
from torch import optim 
import numpy as np 

from contract_bridge.envs.bridge_trick_taking import BridgeEnv
from networks.nn import DQN
from agents.agent import DQNAgent, SmartGreedyAgent, RandomAgent

import random
import os
import sys


def play(team0_agents, team1_agents, env, n_rounds):
    
    players = {}
    players['p_00'] = team0_agents[0]
    players['p_01'] = team0_agents[1]
    players['p_10'] = team1_agents[0]
    players['p_11'] = team1_agents[1]

    team0_wins = 0
    team1_wins = 0

    for round in range(n_rounds):

        #reset the environment with a new random bid
        bid_level = random.randint(7,13)
        bid_trump = random.choice(['C', 'D', 'H', 'S', None])
        bid_trump = None
        bid_team = random.choice([0,1])
        env.reset(bid_level, bid_trump, bid_team)

        for r in range(13):

            for i in range(4):
                pid = env.current_player
                action = players[pid].act()
                env.play({'player': pid, 'card': action})
            
            (_, op_reward, _, _)  = env.step('p_10')
            (_, op_reward, _, _)  = env.step('p_11')
            (_, reward, _, _) = env.step('p_01')
            (_, reward, _, _) = env.step('p_00')
            
            #update the scores on the last trick
            if r==12:
                if reward > op_reward:
                    team0_wins += 1
                else:
                    team1_wins += 1

    env.close()

    print('Team 0 wins: %d, Team 1 wins: %d' % (team0_wins, team1_wins))
    print('Team 0 percentage: %.2f, Team 2 percentage: %.2f' % (team0_wins/n_rounds, team1_wins/n_rounds))


def make_agents(word, team, env):

    pids = ['p_00', 'p_01'] if team==0 else ['p_10', 'p_11']

    if word == 'random':
        return [RandomAgent(pids[0], env), RandomAgent(pids[1], env)]
    elif word == 'smart':
        return [SmartGreedyAgent(pids[0], env), SmartGreedyAgent(pids[1], env)]
    elif word == 'dqn-random':
        return [DQNAgent(pids[0], env, mode='test', policy_dqn='trained_agents/dqn-random.pth'), 
                DQNAgent(pids[1], env, mode='test', policy_dqn='trained_agents/dqn-random.pth')]
    elif word == 'dqn-smart':
        return [DQNAgent(pids[0], env, mode='test', policy_dqn='trained_agents/dqn-smart.pth'), 
                DQNAgent(pids[1], env, mode='test', policy_dqn='trained_agents/dqn-smart.pth')]
    elif word == 'dqn-self-play':
        return [DQNAgent(pids[0], env, mode='test', policy_dqn='trained_agents/dqn-self-play.pth'), 
                DQNAgent(pids[1], env, mode='test', policy_dqn='trained_agents/dqn-self-play.pth')]

    raise Exception()

def run_play(team0_type, team1_type, n_rounds):

    env = gym.make('contract_bridge:contract-bridge-v0')
    team0_agents = make_agents(team0_type, 0, env)
    team1_agents = make_agents(team1_type, 1, env)
    play(team0_agents, team1_agents, env, n_rounds)



if __name__ == '__main__':
    run_play(sys.argv[1], sys.argv[2], int(sys.argv[3]))
