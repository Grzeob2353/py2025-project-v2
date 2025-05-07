# elements/deck.py
import random
from .Card import Card

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in 'shdc' for rank in '23456789JQKA']

    def __str__(self):
        return ' '.join(str(card) for card in self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards):
        return [self.cards.pop() for _ in range(num_cards)]

    def discard_to_bottom(self, card):
        self.cards.insert(0, card)
