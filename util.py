# 通用方法
"""
2020.12.3: update CalBasicScore
"""
from protobuf.message_pb2 import GameResult,GameState
import numpy as np


def CalBasicScore(contract, result, vulnerability):
    """
    计分: 考虑所有情况
    :param: 定约，结果，局况
    :return: 基本分
    """
    contract = contract
    result = result
    suit = contract.suit
    level = contract.level
    score = 0
    exceed_num = result - level - 6
    # 判断是否完成定约
    if result >= level + 6:
        # 完成定约
        basic_score = 20*level if suit == 0 or suit == 1 else 30*level if suit == 2 or suit == 3 else 40 + 30*(level-1)
        if contract.doubled == 0:
            dun_score = basic_score
            double_score = 0
            exceed_score = 20 * exceed_num if suit == 0 or suit == 1 else 30 * exceed_num
        elif contract.doubled == 1:
            dun_score = 2 * basic_score
            double_score = 50
            exceed_score = 100 * exceed_num if vulnerability == 0 or vulnerability == 2 else 200 * exceed_num
        else:
            dun_score = 4 * basic_score
            double_score = 100
            exceed_score = 200 * exceed_num if vulnerability == 0 or vulnerability == 2 else 400 * exceed_num

        game_score = 50 if dun_score < 100 else 300 if vulnerability == 0 or vulnerability == 2 else 500
        if level == 6:
            slam_score = 500 if vulnerability == 0 or vulnerability == 2 else 750
        elif level == 7:
            slam_score = 1000 if vulnerability == 0 or vulnerability == 2 else 1500
        else:
            slam_score = 0

        score = dun_score + game_score + slam_score + exceed_score + double_score
        return score
    else:
        # 罚分
        score = 0
        if contract.doubled == 0:
            return 50*exceed_num if vulnerability == 0 or vulnerability == 2 else 100*exceed_num # 负分
        elif contract.doubled == 1:
            if vulnerability == 0 or vulnerability == 2:
                if exceed_num <= -1 and exceed_num >= -3:
                    score = 100 + (-1*exceed_num-1)*200
                else:
                    score = 500 + (-1*exceed_num-3) * 300
            else:
                score = 200 + (-1*exceed_num - 1) * 300
        else:
            if vulnerability == 0 or vulnerability == 2:
                if exceed_num <= -1 and exceed_num >= -3:
                    score = 200 + (-1*exceed_num-1)*400
                else:
                    score = 1000 + (-1*exceed_num-3) * 600
            else:
                score = 400 + (-1*exceed_num - 1) * 600
        return -1*score

def GameState2feature_cnn(game_state: GameState):
    card_matrix = np.zeros([19,52])
    round_index_feature = [0] * 13
    # round_index
    contract = game_state.contract
    bidding_feature = [0] * 12
    bidding_feature[contract.suit+7] = 1
    bidding_feature[contract.level] = 1
    dun_count_feature = [0] * 2
    desktop_cards_feature = [0] * 52
    remaining_cards_feature = [0] * 52
    round_out_cards_feature = [0] * 52
    open_hand_feature = [0] * 52
    hand_card_feature = [0] * 52
    identity = [0] * 3
    who = game_state.who
    dict_map = {0:0,1:2,2:1,3:2}
    suit_map = {0:3,1:2,2:1,3:0,4:4}
    identity[dict_map[who]] = 1
    playHistorys = game_state.playHistory
    round_index_feature[len(playHistorys)-1] = 1
    history_cards = [[0]*52 for i in range(4)]
    teammate_history_cards = [0]*52
    left_history_cards = [0]*52
    right_history_cards = [0]*52
    self_history_cards = [0]*52
    round_cards = [[0]*52 for i in range(4)]
    teammate_current_trick = [0]*52
    left_current_trick = [0]*52
    right_current_trick = [0]*52
    if len(playHistorys) == 0:
        pass
    else:
        for index, history in enumerate(playHistorys):
            # dun count
            if index != 0 and (history.lead == who or history.lead == (who+2) % 4):
                dun_count_feature[who % 2] += 1
            elif index != 0:
                dun_count_feature[(who+1) % 2] += 1
            else:
                pass

            # history cards
            who_round = history.lead
            # desktop_cards_feature
            for card in history.cards:
                desktop_cards_feature[suit_map[card.suit] * 13 + card.rank] = 1
                card_matrix[index+2,suit_map[card.suit] * 13 + card.rank] = 1
                if index == len(playHistorys) - 1:
                    round_cards[who_round % 4][suit_map[card.suit] * 13 + card.rank] = 1
                history_cards[who_round % 4][suit_map[card.suit] * 13 + card.rank] = 1
                who_round += 1

            # round_out_cards
            if index == len(playHistorys) - 1:
                for card in history.cards:
                    round_out_cards_feature[suit_map[card.suit] * 13 + card.rank] = 1
        teammate_current_trick = round_cards[(2+who) % 4]
        left_current_trick = round_cards[(1+who) % 4]
        right_current_trick = round_cards[(3+who) % 4]
        teammate_history_cards = history_cards[(2+who) % 4]
        left_history_cards = history_cards[(1+who) % 4]
        right_history_cards = history_cards[(3+who) % 4]
        self_history_cards = history_cards[who]

    for card in game_state.hand:
        hand_card_feature[suit_map[card.suit] * 13 + card.rank] = 1

    for card in game_state.dummy:
        open_hand_feature[suit_map[card.suit] * 13 + card.rank] = 1

    sum_card_feature = np.asarray(hand_card_feature) + np.asarray(open_hand_feature) + np.asarray(desktop_cards_feature)
    remaining_cards_feature = list(np.asarray([1]*52) - sum_card_feature)
    cat_feature = round_index_feature + bidding_feature + dun_count_feature + identity + hand_card_feature + open_hand_feature + self_history_cards + teammate_history_cards + left_history_cards + right_history_cards + teammate_current_trick + left_current_trick + right_current_trick

    card_matrix[0, :] = hand_card_feature
    card_matrix[1, :] = open_hand_feature
    card_matrix[15:19, :] = history_cards
    Player = np.zeros([9])
    Player[who] = 1
    Player[suit_map[contract.suit]] = 1
    return card_matrix, Player