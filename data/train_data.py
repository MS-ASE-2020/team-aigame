import json
import multiprocessing
import os
from functools import reduce

import numpy as np
from tqdm import tqdm

from data.DatasetPreprocessing import reverse_Players
from data.dataset import CARD_CLUB, CARD_NUM


def player2num(player: str):
    return reverse_Players[player] - 1


def card2num(card: str):
    club = CARD_CLUB.index(card[0].upper())
    num = CARD_NUM.index(card[1].upper())
    return club * 13 + num


def contract2num(contract: str):
    if contract[-1] == "N":
        return 4
    elif contract[-1] in CARD_CLUB:
        return CARD_CLUB.index(contract[-1])
    else:
        print(f"Error contract {contract}")
        return None


def get_train_data(file_path):
    with open(file_path, 'r') as f:
        file_info = json.load(f)
    process_cart = np.zeros([52, 13])
    process_player = np.zeros([52, 4])
    player_card = np.zeros([4, 52])
    try:
        maker = player2num(file_info["maker"])
    except:
        print(f"Error maker {file_info['maker']}")
        return [[], [], []]
    dummy = (maker + 2) % 4
    contract = contract2num(file_info["contract"])
    if contract == None:
        return [[], [], []]

    # fill palyers' cards
    for player in range(4):
        for card in range(13):
            player_card[player][card2num(file_info["cards"][player][card])] = 1

    # process
    cards = []
    players = []
    ground_truths = []
    for round_num, rounds in enumerate(file_info["rounds"]):
        for process_num in range(len(rounds)):
            try:
                card_present = card2num(rounds[process_num])
            except:
                print(f"Error card {rounds[process_num]}")
                return [[], [], []]
            try:
                present_player = np.argwhere(player_card[:, card_present] == 1)[0][0]
            except:
                print("Error Player doesn't have the card")
                return [[], [], []]
            role = (present_player + 4 - maker) % 4
            # add cards
            card = np.zeros([52, 19])
            card[:, 0] = np.array(player_card[present_player])
            if role == 2:  # dummy
                card[:, 1] = player_card[dummy]
            else:
                card[:, 1] = player_card[maker]
            card[:, 2:15] = process_cart
            card[:, 15:19] = process_player
            cards.append(card)
            # add players
            player = np.zeros([9])
            player[role] = 1  # role
            player[4 + contract] = 1  # contract
            players.append(player)
            # add ground truth
            ground_truth = np.zeros([52])
            ground_truth[card_present] = 1
            ground_truths.append(ground_truth)

            # update process
            process_cart[card_present][round_num] = 1
            process_player[card_present][role] = 1
            player_card[present_player][card_present] = 0

    return [cards, players, ground_truths]


def main():
    data_path = "D:/v-hexin/AIGame"
    file_list = os.listdir(os.path.join(data_path, "data_1024"))
    file_list = [os.path.join(data_path, "data_1024", file) for file in file_list]
    num_core = 72
    if num_core == 1:
        train_data = [[], [], []]
        for file in tqdm(file_list):
            # file_info_name = BlobLister.list_blobs(container)
            file_info = get_train_data(file)
            train_data[0].extend(file_info[0])
            train_data[1].extend(file_info[1])
            train_data[2].extend(file_info[2])
    else:
        pool = multiprocessing.Pool(num_core)
        results = pool.starmap(get_train_data, tqdm([[file] for file in file_list]))
        print('Finish the pool calculate\n')
        pool.close()
        pool.join()
        train_data = reduce(lambda x, y: [x[0] + y[0], x[1] + y[1], x[2] + y[2]], results)
    print(f"Get {len(train_data[0])} train data")
    np.save(os.path.join(data_path, "cards.npy"), np.array(train_data[0]))
    np.save(os.path.join(data_path, "players.npy"), np.array(train_data[1]))
    np.save(os.path.join(data_path, "groun_truth.npy"), np.array(train_data[2]))


if __name__ == '__main__':
    main()
