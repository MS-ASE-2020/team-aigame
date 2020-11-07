import re
from data.DatasetPreprocessing import MakerDef, FirstPlayers, map_Players

CARD_CLUB = ['S', 'H', 'D', 'C']
CARD_NUM = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']


class Game:
    # __slots__ = "url", "id", "cards", "bids", "start_bid", "maker", "contract", "processes", "rounds", "result", "first_players"

    def __init__(self, linurl: str, lin_text: str):
        self.url = linurl
        self.id = lin_text.split('|')[0]
        card_text = re.findall(re.compile("md\|(.*?)\|"), lin_text)[0]
        self.start_bid = map_Players[int(card_text[0])]
        self.cards = get_cards(card_text[1:])
        self.bids = re.findall(re.compile("mb\|(.*?)\|"), lin_text)
        self.maker, self.contract = MakerDef(self.bids, self.start_bid)
        self.processes, self.rounds = get_rounds(lin_text)
        self.first_players = FirstPlayers(self.contract, self.maker if self.maker is not None else self.start_bid,
                                          self.rounds)
        try:
            self.result = re.findall(re.compile("mc\|(.*?)\|"), lin_text)[0]
        except:
            self.result = 13
        self.valid = self.cards is not None and self.processes != []


def get_cards(text: str):
    '''
    To get card info for each players.
    :param text: for example: "S953HAQ97D974C975,SAKQT876HJ4DAK8C4,S2HKT3DQJT52CKQJ2,SJ4H8652D63CAT863"
    :return:for example: [["S9","S5"...],[...],[...],[...]]
    '''
    cards_text = text.split(',')
    cards = []
    used_card = {'S': [0] * 13, 'H': [0] * 13, 'D': [0] * 13, 'C': [0] * 13}
    for card_text in cards_text:
        card = []
        club = CARD_CLUB[0]
        for c in card_text:
            if c in CARD_CLUB:
                club = c
            elif c in CARD_NUM:
                card.append(club + c)
                used_card[club][CARD_NUM.index(c)] = 1
            else:
                print(f"Wrong cards text:{c}")
                return None
        if len(card) == 13:
            cards.append(card)
        else:
            print(f"Wrong card num:{card_text}")
            return None
    if len(cards) == 4:
        return cards
    elif len(cards) == 3:  # Omits the cards of the last player
        card = []
        for club in used_card.keys():
            card.extend(club + CARD_NUM[i] for i in range(len(used_card[club])) if used_card[club][i] == 0)
        if len(card) == 13:
            cards.append(card)
            return cards
        else:
            print(f"Wrong cards num:{text}")
            return None
    else:
        print(f"Wrong cards num:{text}")
        return None


def get_rounds(text: str):
    '''
    To get round info.
    :return: for example: ['cK','cA','c5','c4',...], [['cK','cA','c5','c4'],...]
    '''
    processes = re.findall(re.compile("pc\|(.*?)\|"), text)
    rouds = [processes[i * 4:i * 4 + 4] for i in range(len(processes) // 4)]
    if len(processes) % 4 != 0:
        rouds.append(processes[len(processes) // 4 * 4:])
    return processes, rouds
