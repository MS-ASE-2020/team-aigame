"""
input: which player, the cards in the table, the cards in hand
"""
from functools import cmp_to_key
import numpy as np
from message_pb2 import Hello, HelloResponse, Card, TrickHistory, Contract, GameState, Play, GameResult


def cmp_two_cards(card1: Card, card2: Card, contract: Contract) -> int:
    '''
    比较两张牌大小
    :param card1: 1
    :param card2: 2
    :param contract: 定约
    :return: 1 rep. card1>card2  -1 rep. <  0 rep. =
    '''
    if card1.suit == contract.suit and card2.suit != contract.suit:
        return 1
    elif card1.suit == contract.suit and card2.suit == contract.suit:
        if card1.rank > card2.rank:
            return 1
        elif card1.rank == card2.rank:
            return 0
        else:
            return -1
    elif card1.suit != contract.suit and card2.suit == contract.suit:
        return -1
    else:
        if card1.rank > card2.rank:
            return 1
        elif card1.rank == card2.rank:
            return 0
        else:
            return -1


def get_sorted_card(contract: Contract, validPlays: list, max_: bool) -> Card:
    if contract.suit == 4:  # No trump
        sorted_valid_cards = sorted(validPlays, key=lambda v: v.rank, reverse=max_)
        return sorted_valid_cards[0]  # max_card
    else:
        def cmpp(card1, card2):
            if card1.suit == contract.suit and card2.suit != contract.suit:
                return 1
            elif card1.suit == contract.suit and card2.suit == contract.suit:
                if card1.rank > card2.rank:
                    return 1
                elif card1.rank == card2.rank:
                    return 0
                else:
                    return -1
            elif card1.suit != contract.suit and card2.suit == contract.suit:
                return -1
            else:
                if card1.rank > card2.rank:
                    return 1
                elif card1.rank == card2.rank:
                    return 0
                else:
                    return -1

        sorted_valid_cards = sorted(validPlays, key=cmp_to_key(cmpp), reverse=max_)
        return sorted_valid_cards[0]


def declarer(game_state: GameState, rule: str) -> Card:
    """
    明手
    :param: GameState
    :return: random card
    """
    validPlays = game_state.validPlays  # list for rest valid cards in hand
    if rule == 'random':
        return (validPlays[np.random.randint(len(validPlays))])
    elif rule == 'easy':
        '''
        只分析当前局势，尽量在这一墩得分：出最大的牌，如果最大的没有之前的大，就出最小的
        '''
        contract = game_state.contract
        playHistorys = game_state.playHistory
        trickHistory_new = playHistorys[-1]
        if len(trickHistory_new.cards) == 4:
            # 自己先出
            return get_sorted_card(contract, validPlays, True)
        else:
            max_card = get_sorted_card(contract, validPlays, True)
            max_card_history = max_card
            for card in trickHistory_new.cards:
                if cmp_two_cards(max_card_history, card, contract) == -1:
                    max_card_history = card
            if max_card_history == max_card:
                # max_card最大
                return max_card
            else:
                # 取最小
                return get_sorted_card(contract, validPlays, False)


def lopp(game_state: GameState, rule: str) -> Card:
    """
    防守方1
    :return: random card
    """
    validPlays = game_state.validPlays  # list for rest valid cards in hand
    if rule == 'random':
        return (validPlays[np.random.randint(len(validPlays))])
    elif rule == 'easy':
        '''
        只分析当前局势，尽量在这一墩得分：出最大的牌，如果最大的没有之前的大，就出最小的
        '''
        contract = game_state.contract
        playHistorys = game_state.playHistory
        trickHistory_new = playHistorys[-1]
        if len(trickHistory_new.cards) == 4:
            # 自己先出
            return get_sorted_card(contract, validPlays, True)
        else:
            max_card = get_sorted_card(contract, validPlays, True)
            max_card_history = max_card
            for card in trickHistory_new.cards:
                if cmp_two_cards(max_card_history, card, contract) == -1:
                    max_card_history = card
            if max_card_history == max_card:
                # max_card最大
                return max_card
            else:
                # 取最小
                return get_sorted_card(contract, validPlays, False)


def dummy(game_state: GameState, rule: str) -> Card:
    """
    防守方2
    :return: random card
    """
    validPlays = game_state.validPlays  # list for rest valid cards in hand
    if rule == 'random':
        return (validPlays[np.random.randint(len(validPlays))])
    elif rule == 'easy':
        '''
        只分析当前局势，尽量在这一墩得分：出最大的牌，如果最大的没有之前的大，就出最小的
        '''
        contract = game_state.contract
        playHistorys = game_state.playHistory
        trickHistory_new = playHistorys[-1]
        if len(trickHistory_new.cards) == 4:
            # 自己先出
            return get_sorted_card(contract, validPlays, True)
        else:
            max_card = get_sorted_card(contract, validPlays, True)
            max_card_history = max_card
            for card in trickHistory_new.cards:
                if cmp_two_cards(max_card_history, card, contract) == -1:
                    max_card_history = card
            if max_card_history == max_card:
                # max_card最大
                return max_card
            else:
                # 取最小
                return get_sorted_card(contract, validPlays, False)


def ropp(game_state: GameState, rule: str) -> Card:
    """
    庄家
    Current_Cards: cards in this round (sorted)
    Hand_Cards: cards in hand
    History_Cards: cards in the table
    :return: random card
    """
    validPlays = game_state.validPlays  # list for rest valid cards in hand
    if rule == 'random':
        return (validPlays[np.random.randint(len(validPlays))])
    elif rule == 'easy':
        '''
        只分析当前局势，尽量在这一墩得分：出最大的牌，如果最大的没有之前的大，就出最小的
        '''
        contract = game_state.contract
        playHistorys = game_state.playHistory
        trickHistory_new = playHistorys[-1]
        if len(trickHistory_new.cards) == 4:
            # 自己先出
            return get_sorted_card(contract, validPlays, True)
        else:
            max_card = get_sorted_card(contract, validPlays, True)
            max_card_history = max_card
            for card in trickHistory_new.cards:
                if cmp_two_cards(max_card_history, card, contract) == -1:
                    max_card_history = card
            if max_card_history == max_card:
                # max_card最大
                return max_card
            else:
                # 取最小
                return get_sorted_card(contract, validPlays, False)
