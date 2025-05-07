# elements/player.py
class Player:
    def __init__(self, money, name=""):
        self.stack = money
        self.name = name
        self.hand = []

    def take_card(self, card):
        self.hand.append(card)

    def get_stack_amount(self):
        return self.stack

    def change_card(self, card, idx):
        old_card = self.hand[idx]
        self.hand[idx] = card
        return old_card

    def get_player_hand(self):
        return tuple(sorted(self.hand, key=lambda card: card.value(), reverse=True))

    def cards_to_str(self):
        sorted_hand = sorted(self.hand, key=lambda card: card.value(), reverse=True)
        return ' '.join(str(card) for card in sorted_hand)
