"""
此script主要是包含两个接口
1. 通过输入的.Lin文件返回每一副牌的庄家
2. 对于每一轮出牌，返回第一个出牌的玩家
"""

map_Players = {0: 'E', 1: 'S', 2: 'W', 3: 'N', 4: 'E'}
reverse_Players = {'S': 1, 'W': 2, 'N': 3, 'E': 4}


def map_players(input):
    return map_Players[input]


def MakerDef(Bids, StartBid):
    """
    定庄家, 之前搞错了,应该还是需要遍历一下，可以先定哪一对定了多高的定约，然后再定是哪一家
    :param Bids: 希望格式是['p','1S',...,'p','p','p']
    :param StartBid: 1:S, 2:W, 3:N, 4:E
    :return: 1:S, 2:W, 3:N, 4:E and Contract
    """
    bid_nums = len(Bids)
    bid_end = StartBid + bid_nums - 1
    find_contract = False
    bid_result = 'p'
    maker = None
    for i, bid in enumerate(reversed(Bids)):
        if bid != 'p' and bid != 'x' and bid != '2x' and find_contract is False:
            bid_result = bid
            maker = bid_end % 4
            find_contract = True
        if find_contract and bid[-1] == bid_result[-1] and (bid_end % 4 == maker or bid_end % 4 == (maker + 2) % 4):
            maker = bid_end % 4
        bid_end -= 1
    if not find_contract:  # 4 pass
        maker = None  # 无庄家
    else:
        maker = map_Players[maker]
    return maker, bid_result


def FirstPlayers(contract, maker, play_processes):
    """
    给定定约，庄家以及打牌过程得到每一轮首出牌的人
    :param contract: 1C,1D,1H,1S,1NT...
    :param maker: 1,2,3,4
    :param play_processes: 希望是list[list] such as: [['cK','cA','c5','c4'],...]
    :return: [每轮首次出牌的方]
    """
    first = [(maker + 1) % 4]  # 首攻
    for process in play_processes[:-1]:
        max_value = process[0]
        for index, card in enumerate(process[1:]):
            if 'NT' in contract:
                # 无将判断
                if max_value[0] != card[0]:
                    # 不同花色
                    continue
                else:
                    if '--23456789TJQKA'.index(max_value[1]) < '--23456789TJQKA'.index(card[1]):
                        max_value = card
                    else:
                        continue
            else:
                # 有将
                if max_value[0] not in contract:
                    # 出的牌不是将牌
                    if max_value[0] != card[0] and card[0] not in contract:
                        continue
                    elif max_value[0] != card[0] and card[0] in contract:
                        max_value = card
                    elif max_value[0] == card[0]:
                        if '--23456789TJQKA'.index(max_value[1]) < '--23456789TJQKA'.index(card[1]):
                            max_value = card
                        else:
                            continue
                else:
                    # 出的牌是将牌
                    if max_value[0] != card[0]:
                        continue
                    else:
                        if '--23456789TJQKA'.index(max_value[1]) < '--23456789TJQKA'.index(card[1]):
                            max_value = card
                        else:
                            continue
        max_index = process.index(max_value)
        first.append((first[-1] + max_index) % 4)
    return [map_Players[x] for x in first]
