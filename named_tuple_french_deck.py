from collections import namedtuple

Card = namedtuple('Card', ['rank', 'suit'])


class FrenchDeck:
    ranks = [str(i) for i in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._deck = [Card(rank, suit) for suit in self.suits for rank in self.ranks]

    def __getitem__(self, index):
        return self._deck[index]

    def __len__(self):
        return len(self._deck)


deck = FrenchDeck()

suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)


def spades_high(card):
    rank_value = FrenchDeck.ranks.index(card.rank)
    return rank_value * len(suit_values) + suit_values[card.suit]


for card in sorted(deck, key=spades_high):
    print(card)
