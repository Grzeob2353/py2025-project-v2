class Card:
    unicode_dict = {'s': '\u2660', 'h': '\u2665', 'd': '\u2666', 'c': '\u2663'}
    value_order = {r: i for i, r in enumerate("23456789JQKA", start=2)}

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def get_value(self):
        return (self.rank, self.suit)

    def value(self):
        return self.value_order[self.rank]

    def __str__(self):
        return f"{self.rank}{self.unicode_dict[self.suit]}"
