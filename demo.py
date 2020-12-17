"""
input: which player, the cards in the table, the cards in hand
add opp 首攻，第二家，第三家出牌原则 2020.11.22
"""
from functools import cmp_to_key
import numpy as np
from protobuf.message_pb2 import Hello, HelloResponse, Card, TrickHistory, Contract, GameState, Play, GameResult


def cmp_two_cards(card1: Card, card2: Card, contract: Contract, tmp_contract = None) -> int:
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
        if tmp_contract == None:
            if card1.rank > card2.rank:
                return 1
            elif card1.rank == card2.rank:
                return 0
            else:
                return -1
        else:
            if card1.suit == tmp_contract.suit and card2.suit != tmp_contract.suit:
                return 1
            elif card1.suit == tmp_contract.suit and card2.suit == tmp_contract.suit:
                if card1.rank > card2.rank:
                    return 1
                elif card1.rank == card2.rank:
                    return 0
                else:
                    return -1
            elif card1.suit != tmp_contract.suit and card2.suit == tmp_contract.suit:
                return -1


def get_sorted_card(contract: Contract, validPlays: list, max_: bool) -> Card:
    if contract.suit == 4:  # No trump
        sorted_valid_cards = sorted(validPlays, key=lambda v: v.rank, reverse=max_)
        return sorted_valid_cards[0]  # max_card
    else:
        def cmpp(card1, card2):
            if card1.suit == contract.suit and card2.suit != contract.suit:
                return 1
            elif card1.suit ==\
                    contract.suit and card2.suit == contract.suit:
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


def get_sorted_cards(contract: Contract, validPlays: list, max_: bool) -> Card:
    if contract.suit == 4:  # No trump
        sorted_valid_cards = sorted(validPlays, key=lambda v: v.rank, reverse=max_)
        return sorted_valid_cards  # max_card
    else:
        def cmpp(card1, card2):
            if card1.suit == contract.suit and card2.suit != contract.suit:
                return 1
            elif card1.suit ==\
                    contract.suit and card2.suit == contract.suit:
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
        return sorted_valid_cards


def get_suits_from_cards(validPlays: list) -> dict:
    """
    从手牌中获得每种花色的牌，返回字典{'C':,'D',...}
    :param validPlays:
    :return: dict
    """
    hand_card = {0: [], 1: [], 2: [],3: []}
    for card in validPlays:
        hand_card[card.suit].append(card)
    return hand_card


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
        trickHistory_new = playHistorys[-1] if len(playHistorys) > 0 else None
        if trickHistory_new is None or len(trickHistory_new.cards) == 4:
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
    elif rule == 'hard':
        contract = game_state.contract
        dummy_card = game_state.dummy
        hand_card = validPlays
        playHistorys = game_state.playHistory
        trickHistory_new = playHistorys[-1] if len(playHistorys) > 0 else None
        # sorted_hand_cards = get_sorted_cards(contract,validPlays,True)
        # 庄家需要考虑飞牌，防止大牌被进手，其实可以考虑通过明手和自己手牌进行分析，计算赢墩或者输墩，然后打牌，但感觉很难用code描述
        if len(trickHistory_new.cards) == 4:
            #第一个出牌,可以考虑出长套和点数大的套，如果dummy有大牌（比如J以上），那就出小，否则出大
            dummy_suits = get_suits_from_cards(dummy_card)
            hand_suits = get_suits_from_cards(hand_card)
            len_suits = []
            for i in range(4):
                len_suits.append(len(dummy_suits[i])+len(hand_suits[i]))
            max_len_suit = len_suits.index(max(len_suits))
            # 考虑出长套
            for card in dummy_suits[max_len_suit]:
                if card.rank > 9 and len(hand_suits[max_len_suit]) >= 1:
                    return get_sorted_card(contract, hand_suits[max_len_suit], False)
            return get_sorted_card(contract, hand_suits[max_len_suit], True) if len(hand_suits[max_len_suit]) >=1 else get_sorted_card(contract, validPlays, True)
        elif len(trickHistory_new.cards) == 1:
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            sorted_hand_cards = get_sorted_cards(tmp_contract, validPlays, True)
            if cmp_two_cards(sorted_hand_cards[0],trickHistory_new.cards[0],tmp_contract) == 1:
                return sorted_hand_cards[0]
            else:
                return sorted_hand_cards[-1]
        elif len(trickHistory_new.cards) == 2:
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            sorted_hand_cards = get_sorted_cards(tmp_contract, validPlays, True)
            if cmp_two_cards(trickHistory_new.cards[1],trickHistory_new.cards[0],tmp_contract) == 1:
                if len(sorted_hand_cards)>=2 and cmp_two_cards(sorted_hand_cards[1], trickHistory_new.cards[1],tmp_contract) == 1:
                    return sorted_hand_cards[1]
                elif cmp_two_cards(sorted_hand_cards[0], trickHistory_new.cards[1],tmp_contract) == 1:
                    return sorted_hand_cards[0]
                else:
                    return sorted_hand_cards[-1]
            else:
                return sorted_hand_cards[-1]#sorted_hand_cards[1] if len(sorted_hand_cards)>=2 else sorted_hand_cards[0]
        else:
            # 第四家打牌: 如果同伴的牌已经打过了庄家，那么出最小，否则出按照有大出大，否则出小
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            if cmp_two_cards(trickHistory_new.cards[1], trickHistory_new.cards[0], tmp_contract) == 1 and \
                    cmp_two_cards(trickHistory_new.cards[1], trickHistory_new.cards[2], tmp_contract) == 1:
                return get_sorted_card(tmp_contract, validPlays, False)
            else:
                max_card = get_sorted_card(tmp_contract, validPlays, True)
                if cmp_two_cards(max_card, trickHistory_new.cards[0], tmp_contract) == 1 and \
                        cmp_two_cards(max_card, trickHistory_new.cards[2], tmp_contract) == 1:
                    return max_card
                else:
                    # 取最小
                    return get_sorted_card(tmp_contract, validPlays, False)


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
        trickHistory_new = playHistorys[-1] if len(playHistorys) > 0 else None
        if trickHistory_new is None or len(trickHistory_new.cards) == 4:
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
    elif rule == 'hard':
        # 防守方
        contract = game_state.contract
        playHistorys = game_state.playHistory
        trickHistory_new = playHistorys[-1] if len(playHistorys) > 0 else None
        if trickHistory_new is None:
            # 首攻
            hand_card = get_suits_from_cards(validPlays)
            if contract.suit == 4:
                #先考虑无将,攻长四
                max_len = 0
                attack_suits = []
                for i in range(4):
                    if max_len < len(hand_card[i]):
                        attack_suits = hand_card[i]
                        max_len = len(hand_card[i])
                # 长四
                return sorted(attack_suits, key=lambda v: v.rank, reverse=True)[3]
            else:
                return get_sorted_card(contract, validPlays, True)
        elif len(trickHistory_new.cards) == 4:
            return get_sorted_card(contract, validPlays, True)
        elif len(trickHistory_new.cards) == 1:
            # 第二家打牌: 原则：第二家打小牌和大牌盖大牌
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            if trickHistory_new.cards[0].rank <= 10:
                # 出最小的牌
                return get_sorted_card(tmp_contract, validPlays, False)
            else:
                # 用大牌盖，如果没有，出最小
                sorted_cards = get_sorted_cards(tmp_contract, validPlays, True)
                if cmp_two_cards(sorted_cards[0], trickHistory_new.cards[0],tmp_contract) == 1:
                    # 可以大
                    return sorted_cards[0]
                else:
                    # 出最小
                    return sorted_cards[-1]
        elif len(trickHistory_new.cards) == 2:
            # 第三家打牌: 分为两种情况，一种是长四的对应出牌，一种是第三家打大牌原则，不过貌似都应该出最大的牌，一是为了防止阻塞，二是为了赢墩
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            if get_sorted_card(contract,validPlays,True).suit == tmp_contract.suit:
                sorted_cards = get_sorted_cards(tmp_contract, validPlays, True)
                if cmp_two_cards(trickHistory_new.cards[0], trickHistory_new.cards[1], tmp_contract) == 1:
                    return get_sorted_card(contract, validPlays, False)
                if cmp_two_cards(sorted_cards[0], trickHistory_new.cards[1], tmp_contract) == 1:
                    return sorted_cards[0]
                else:
                    return sorted_cards[1] if len(sorted_cards) > 1 else sorted_cards[0]
            else:
                return get_sorted_card(contract, validPlays, False)
        else:
            # 第四家打牌: 如果同伴的牌已经打过了庄家，那么出最小，否则出按照有大出大，否则出小
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            if cmp_two_cards(trickHistory_new.cards[1], trickHistory_new.cards[0], tmp_contract) == 1 and \
                    cmp_two_cards(trickHistory_new.cards[1], trickHistory_new.cards[2], tmp_contract) == 1:
                return get_sorted_card(tmp_contract, validPlays, False)
            else:
                max_card = get_sorted_card(tmp_contract, validPlays, True)
                if cmp_two_cards(max_card, trickHistory_new.cards[0], tmp_contract) == 1 and \
                        cmp_two_cards(max_card, trickHistory_new.cards[2], tmp_contract) == 1:
                    return max_card
                else:
                    # 取最小
                    return get_sorted_card(tmp_contract, validPlays, False)


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
        trickHistory_new = playHistorys[-1] if len(playHistorys) > 0 else None
        if trickHistory_new is None or len(trickHistory_new.cards) == 4:
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
    elif rule == 'hard':
        contract = game_state.contract
        dummy_card = game_state.dummy
        hand_card = validPlays
        playHistorys = game_state.playHistory
        trickHistory_new = playHistorys[-1] if len(playHistorys) > 0 else None
        # sorted_hand_cards = get_sorted_cards(contract,validPlays,True)
        # 庄家需要考虑飞牌，防止大牌被进手，其实可以考虑通过明手和自己手牌进行分析，计算赢墩或者输墩，然后打牌，但感觉很难用code描述
        if len(trickHistory_new.cards) == 4:
            # 第一个出牌,可以考虑出长套和点数大的套，如果dummy有大牌（比如J以上），那就出小，否则出大
            dummy_suits = get_suits_from_cards(dummy_card)
            hand_suits = get_suits_from_cards(hand_card)
            len_suits = []
            for i in range(4):
                len_suits.append(len(dummy_suits[i]) + len(hand_suits[i]))
            max_len_suit = len_suits.index(max(len_suits))
            # 考虑出长套
            for card in dummy_suits[max_len_suit]:
                if card.rank > 10 and len(hand_suits[max_len_suit]) >= 1:
                    return get_sorted_card(contract, hand_suits[max_len_suit], False)
            return get_sorted_card(contract, hand_suits[max_len_suit], True) if len(hand_suits[max_len_suit]) >=1 else get_sorted_card(contract, validPlays, True)
        elif len(trickHistory_new.cards) == 1:
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            sorted_hand_cards = get_sorted_cards(tmp_contract, validPlays, True)
            if cmp_two_cards(sorted_hand_cards[0], trickHistory_new.cards[0], tmp_contract) == 1:
                return sorted_hand_cards[0]
            else:
                return sorted_hand_cards[-1]
        elif len(trickHistory_new.cards) == 2:
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            sorted_hand_cards = get_sorted_cards(tmp_contract, validPlays, True)
            if cmp_two_cards(trickHistory_new.cards[1], trickHistory_new.cards[0], tmp_contract) == 1:
                if len(sorted_hand_cards) >= 2 and cmp_two_cards(sorted_hand_cards[1], trickHistory_new.cards[1],
                                                                 tmp_contract) == 1:
                    return sorted_hand_cards[1]
                elif cmp_two_cards(sorted_hand_cards[0], trickHistory_new.cards[1], tmp_contract) == 1:
                    return sorted_hand_cards[0]
                else:
                    return sorted_hand_cards[-1]
            else:
                return sorted_hand_cards[-1]#sorted_hand_cards[1] if len(sorted_hand_cards)>=2 else sorted_hand_cards[0]
        else:
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            max_card = get_sorted_card(tmp_contract, validPlays, True)
            max_card_history = max_card
            for card in trickHistory_new.cards:
                if cmp_two_cards(max_card_history, card, tmp_contract) == -1:
                    max_card_history = card
            if max_card_history == max_card:
                # max_card最大
                return max_card
            else:
                # 取最小
                return get_sorted_card(tmp_contract, validPlays, False)
        # sorted_hand_cards = get_sorted_cards(contract,validPlays,True)
        # # 庄家需要考虑飞牌，防止大牌被进手，其实可以考虑通过明手和自己手牌进行分析，计算赢墩或者输墩，然后打牌，但感觉很难用code描述
        # if len(trickHistory_new.cards) == 4:
        #     #第一个出牌,可以考虑出长套和点数大的套，如果dummy有大牌（比如J以上），那就出小，否则出大
        #     dummy_suits = get_suits_from_cards(dummy_card)
        #     hand_suits = get_suits_from_cards(hand_card)
        #     len_suits = []
        #     for i in range(4):
        #         len_suits.append(len(dummy_suits[i])+len(hand_suits[i]))
        #     max_len_suit = len_suits.index(max(len_suits))
        #     # 考虑出长套
        #     for card in dummy_suits[max_len_suit]:
        #         if card.rank > 10:
        #             return get_sorted_card(contract,hand_suits[max_len_suit],False)
        #     return get_sorted_card(contract, hand_suits[max_len_suit],True)
        # elif len(trickHistory_new.cards) == 1:
        #     if cmp_two_cards(sorted_hand_cards[0],trickHistory_new.cards[0],contract) == 1:
        #         return sorted_hand_cards[0]
        #     else:
        #         return sorted_hand_cards[-1]
        # elif len(trickHistory_new.cards) == 2:
        #     if cmp_two_cards(trickHistory_new.cards[1],trickHistory_new.cards[0],contract) == 1:
        #         if cmp_two_cards(sorted_hand_cards[1], trickHistory_new.cards[1],contract) == 1:
        #             return sorted_hand_cards[1]
        #         elif cmp_two_cards(sorted_hand_cards[0], trickHistory_new.cards[1],contract) == 1:
        #             return sorted_hand_cards[0]
        #         else:
        #             return sorted_hand_cards[-1]
        #     else:
        #         return sorted_hand_cards[1]
        # else:
        #     max_card = get_sorted_card(contract, validPlays, True)
        #     max_card_history = max_card
        #     for card in trickHistory_new.cards:
        #         if cmp_two_cards(max_card_history, card, contract) == -1:
        #             max_card_history = card
        #     if max_card_history == max_card:
        #         # max_card最大
        #         return max_card
        #     else:
        #         # 取最小
        #         return get_sorted_card(contract, validPlays, False)


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
        trickHistory_new = playHistorys[-1] if len(playHistorys) > 0 else None
        if trickHistory_new is None or len(trickHistory_new.cards) == 4:
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
    elif rule == 'hard':
        # 防守方
        contract = game_state.contract
        playHistorys = game_state.playHistory
        trickHistory_new = playHistorys[-1] if len(playHistorys) > 0 else None
        if trickHistory_new is None:
            # 首攻
            hand_card = get_suits_from_cards(validPlays)
            if contract.suit == 4:
                # 先考虑无将,攻长四
                max_len = 0
                attack_suits = []
                for i in range(4):
                    if max_len < len(hand_card[i]):
                        attack_suits = hand_card[i]
                        max_len = len(hand_card[i])
                # 长四
                return sorted(attack_suits, key=lambda v: v.rank, reverse=True)[3]
            else:
                return get_sorted_card(contract, validPlays, True)
        elif len(trickHistory_new.cards) == 4:
            return get_sorted_card(contract, validPlays, True)
        elif len(trickHistory_new.cards) == 1:
            # 第二家打牌: 原则：第二家打小牌和大牌盖大牌
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            if trickHistory_new.cards[0].rank <= 10:
                # 出最小的牌
                return get_sorted_card(tmp_contract, validPlays, False)
            else:
                # 用大牌盖，如果没有，出最小
                sorted_cards = get_sorted_cards(tmp_contract, validPlays, True)
                if cmp_two_cards(sorted_cards[0], trickHistory_new.cards[0], tmp_contract) == 1:
                    # 可以大
                    return sorted_cards[0]
                else:
                    # 出最小
                    return sorted_cards[-1]
        elif len(trickHistory_new.cards) == 2:
            # 第三家打牌: 分为两种情况，一种是长四的对应出牌，一种是第三家打大牌原则，不过貌似都应该出最大的牌，一是为了防止阻塞，二是为了赢墩
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            if get_sorted_card(contract, validPlays, True).suit == tmp_contract.suit:
                sorted_cards = get_sorted_cards(tmp_contract, validPlays, True)
                if cmp_two_cards(trickHistory_new.cards[0], trickHistory_new.cards[1], tmp_contract) == 1:
                    return get_sorted_card(contract, validPlays, False)
                if cmp_two_cards(sorted_cards[0], trickHistory_new.cards[1], tmp_contract) == 1:
                    return sorted_cards[0]
                else:
                    return sorted_cards[1] if len(sorted_cards) > 1 else sorted_cards[0]
            else:
                return get_sorted_card(contract, validPlays, False)
        else:
            # 第四家打牌: 如果同伴的牌已经打过了庄家，那么出最小，否则出按照有大出大，否则出小
            tmp_contract = Contract()
            tmp_contract.suit = trickHistory_new.cards[0].suit
            if cmp_two_cards(trickHistory_new.cards[1], trickHistory_new.cards[0], tmp_contract) == 1 and \
                    cmp_two_cards(trickHistory_new.cards[1], trickHistory_new.cards[2], tmp_contract) == 1:
                return get_sorted_card(tmp_contract, validPlays, False)
            else:
                max_card = get_sorted_card(tmp_contract, validPlays, True)
                if cmp_two_cards(max_card, trickHistory_new.cards[0], tmp_contract) == 1 and \
                        cmp_two_cards(max_card, trickHistory_new.cards[2], tmp_contract) == 1:
                    return max_card
                else:
                    # 取最小
                    return get_sorted_card(tmp_contract, validPlays, False)
