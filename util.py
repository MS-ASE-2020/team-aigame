# 通用方法
from protobuf.message_pb2 import GameResult

def CalBasicScore(gameResult: GameResult):
    """
    计分: 考虑无局不加倍
    :param gameResult: protobuf data
    :return: 基本分
    """
    contract = gameResult.contract
    result = gameResult.result
    suit = contract.suit
    level = contract.level
    score = 0
    # 判断是否完成定约
    if result >= level + 6:
        # 完成
        basic_score = 20*level if suit == 0 or suit == 1 else 30*level if suit == 2 or suit == 3 else 40 + 30*(level-1)
        game_score = 50 if basic_score < 100 else 300
        slam_score = 500 if level == 6 else 1000 if level == 7 else 0
        exceed_score = 20*(result-level-6) if suit == 0 or suit == 1 else 30*(result-level-6)
        score = basic_score + game_score + slam_score + exceed_score
        return score
    else:
        # 罚分
        return 50*(level + 6 - result)