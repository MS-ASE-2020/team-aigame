# 通用方法
"""
2020.12.3: update CalBasicScore
"""
from protobuf.message_pb2 import GameResult

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

