from protobuf.protobuf_modify.message1_pb2 import GameResult,GameState
import numpy as np

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
    return np.concatenate((card_matrix.flatten(),Player))


def GameState2feature_MLP(game_state: GameState):
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
    identity[dict_map[who]] = 1
    playHistorys = game_state.playHistory
    round_index_feature[len(playHistorys)-1] = 1
    if len(playHistorys) == 0:
        pass
    else:
        for index, history in enumerate(playHistorys):
            # dun count
            if index != 0 and (history.lead == who or history.lead == (who+2) % 4):
                dun_count_feature[who % 2] += 1
            elif index != 0:
                dun_count_feature[(who + 1) % 2] += 1
            else:
                pass

            # desktop_cards_feature
            for card in history.cards:
                desktop_cards_feature[card.suit * 13 + card.rank] = 1

            # round_out_cards
            if index == len(playHistorys) - 1:
                for card in history.cards:
                    round_out_cards_feature[card.suit * 13 + card.rank] = 1
    for card in game_state.hand:
        hand_card_feature[card.suit * 13 + card.rank] = 1

    for card in game_state.dummy:
        open_hand_feature[card.suit * 13 + card.rank] = 1

    sum_card_feature = np.asarray(hand_card_feature) + np.asarray(open_hand_feature) + np.asarray(desktop_cards_feature)
    remaining_cards_feature = list(np.asarray([1]*52) - sum_card_feature)
    cat_feature = round_index_feature + bidding_feature + dun_count_feature + identity + hand_card_feature + open_hand_feature + desktop_cards_feature + remaining_cards_feature + round_out_cards_feature
    return cat_feature


def GameState2feature_DQN(game_state: GameState):
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
                desktop_cards_feature[card.suit * 13 + card.rank] = 1
                if index == len(playHistorys) - 1:
                    round_cards[who_round % 4][card.suit * 13 + card.rank] = 1
                history_cards[who_round % 4][card.suit * 13 + card.rank] = 1
                who_round += 1

            # round_out_cards
            if index == len(playHistorys) - 1:
                for card in history.cards:
                    round_out_cards_feature[card.suit * 13 + card.rank] = 1
        teammate_current_trick = round_cards[(2+who) % 4]
        left_current_trick = round_cards[(1+who) % 4]
        right_current_trick = round_cards[(3+who) % 4]
        teammate_history_cards = history_cards[(2+who) % 4]
        left_history_cards = history_cards[(1+who) % 4]
        right_history_cards = history_cards[(3+who) % 4]
        self_history_cards = history_cards[who]

    for card in game_state.hand:
        hand_card_feature[card.suit * 13 + card.rank] = 1

    for card in game_state.dummy:
        open_hand_feature[card.suit * 13 + card.rank] = 1
    # print(teammate_current_trick,teammate_history_cards)
    sum_card_feature = np.asarray(hand_card_feature) + np.asarray(open_hand_feature) + np.asarray(desktop_cards_feature)
    remaining_cards_feature = list(np.asarray([1]*52) - sum_card_feature)
    cat_feature = round_index_feature + bidding_feature + dun_count_feature + identity + hand_card_feature + open_hand_feature + self_history_cards + teammate_history_cards + left_history_cards + right_history_cards + teammate_current_trick + left_current_trick + right_current_trick
    return cat_feature
    