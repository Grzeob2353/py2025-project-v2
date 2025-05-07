# elements/game_engine.py
from .Deck import Deck
from .Player import Player

class GameEngine:
    def __init__(self, players, deck, small_blind=25, big_blind=50):
        self.players = players
        self.deck = deck
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.pot = 0
        self.active_players = players.copy()

    def play_round(self):
        self.deck.shuffle()
        self.collect_blinds()
        self.deal_cards()
        self.betting_round()
        self.exchange_phase()
        self.showdown()

    def collect_blinds(self):
        sb_player = self.players[0]
        bb_player = self.players[1 % len(self.players)]
        sb_player.stack -= self.small_blind
        bb_player.stack -= self.big_blind
        self.pot += self.small_blind + self.big_blind
        print(f"{sb_player.name} pays small blind: {self.small_blind}")
        print(f"{bb_player.name} pays big blind: {self.big_blind}")

    def deal_cards(self):
        for player in self.players:
            player.hand = self.deck.deal(5)
            print(f"\nKarty gracza {player.name}: {player.cards_to_str()}")

    def betting_round(self):
        current_bet = self.big_blind
        for player in self.active_players:
            print(f"\n{player.name}, aktualna stawka: {current_bet}, twój stack: {player.stack}")
            while True:
                action = input("Wybierz akcję (call, raise, fold): ").strip().lower()
                if action == "call":
                    bet = current_bet
                    break
                elif action == "raise":
                    try:
                        raise_amount = int(input("Podaj kwotę podbicia: "))
                        bet = current_bet + raise_amount
                        current_bet = bet
                        break
                    except ValueError:
                        print("Nieprawidłowa kwota.")
                elif action == "fold":
                    self.active_players.remove(player)
                    print(f"{player.name} spasował.")
                    return
                else:
                    print("Nieprawidłowa akcja.")
            player.stack -= bet
            self.pot += bet
            print(f"{player.name} betuje {bet}.")

    def exchange_phase(self):
        for player in self.active_players:
            print(f"\nKarty przed wymianą ({player.name}): {player.cards_to_str()}")
            indices_input = input(f"{player.name}, podaj indeksy kart do wymiany (np. 0 3 4), lub ENTER żeby pominąć: ")
            if indices_input.strip() == "":
                continue
            try:
                indices = list(map(int, indices_input.strip().split()))
                for idx in indices:
                    if 0 <= idx < 5:
                        old_card = player.hand[idx]
                        new_card = self.deck.deal(1)[0]
                        player.hand[idx] = new_card
                        self.deck.discard_to_bottom(old_card)
                    else:
                        print(f"Nieprawidłowy indeks: {idx}")
                print(f"Karty po wymianie: {player.cards_to_str()}")
            except ValueError:
                print("Nieprawidłowe dane wejściowe.")

    def hand_value(self, hand):
        value_map = {r: i for i, r in enumerate("23456789TJQKA", start=2)}
        values = [card.rank for card in hand]
        suits = [card.suit for card in hand]
        counts = {v: values.count(v) for v in set(values)}
        val_counts = sorted(counts.items(), key=lambda x: (-x[1], -value_map[x[0]]))
        sorted_vals = sorted([value_map[v] for v in values], reverse=True)
        is_flush = len(set(suits)) == 1
        is_straight = sorted_vals == list(range(sorted_vals[0], sorted_vals[0] - 5, -1))
        if is_straight and is_flush:
            return (9, sorted_vals, "Straight Flush")
        elif val_counts[0][1] == 4:
            return (8, sorted_vals, "Four of a Kind")
        elif val_counts[0][1] == 3 and val_counts[1][1] == 2:
            return (7, sorted_vals, "Full House")
        elif is_flush:
            return (6, sorted_vals, "Flush")
        elif is_straight:
            return (5, sorted_vals, "Straight")
        elif val_counts[0][1] == 3:
            return (4, sorted_vals, "Three of a Kind")
        elif val_counts[0][1] == 2 and val_counts[1][1] == 2:
            return (3, sorted_vals, "Two Pair")
        elif val_counts[0][1] == 2:
            return (2, sorted_vals, "One Pair")
        else:
            return (1, sorted_vals, "High Card")

    def showdown(self):
        best_value = (0, [])
        winner = None
        print("\n--- SHOWDOWN ---")
        for player in self.active_players:
            strength, kicker, combination = self.hand_value(player.hand)
            print(f"{player.name} ma: {player.cards_to_str()} — {combination}")
            if strength > best_value[0] or (strength == best_value[0] and kicker > best_value[1]):
                best_value = (strength, kicker)
                winner = player
        if winner:
            winner.stack += self.pot
            print(f"\nZwycięzca: {winner.name}, otrzymuje {self.pot} żetonów.")
        else:
            print("\nBrak zwycięzcy.")
