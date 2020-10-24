"""
input: which player, the cards in the table, the cards in hand
"""
import numpy as np

def NorthPlayer():
    """
    明手
    :return: random card
    """
    pass


def WestPlayer():
    """
    防守方1
    :return: random card
    """
    pass


def EastPlayer():
    """
    防守方2
    :return: random card
    """
    pass


def SouthPlayer(Current_Cards, Hand_Cards, History_Cards, Dummy_Cards):
    """
    庄家
    Current_Cards: cards in this round (sorted)
    Hand_Cards: cards in hand
    History_Cards: cards in the table
    :return: random card
    """
    # random
    if len(Current_Cards) == 0:
        # 自己出牌, 根据明手信息出牌
        np.random()


