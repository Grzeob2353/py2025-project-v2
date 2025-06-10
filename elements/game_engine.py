from .Deck import Deck
from .Player import Player
from .Card import Card
from .bot_player import BotPlayer


class GameEngine:
    def __init__(self, players, deck, small_blind=25, big_blind=50):
        self.all_players = players
        self.deck = deck
        self.small_blind = small_blind
        self.big_blind = big_blind

        self.pot = 0
        self.active_players = []
        self.bets_this_round = {}
        self.current_bet_to_call = 0
        self.min_raise_amount = 0
        self.last_raiser = None

        self.log = []
        self.game_phase = None
        self.current_player_idx = -1

    def start_new_round(self):
        self.log.clear()
        self.log.append("--- Nowa Runda ---")

        self.active_players = [p for p in self.all_players if p.get_stack_amount() > 0]
        if len(self.active_players) < 2:
            self.game_phase = 'game-over'
            self.log.append("Koniec gry! Za mało graczy.")
            return

        # Resetuj stan rundy
        self.pot = 0
        self.deck = Deck()
        self.deck.shuffle()
        self.bets_this_round = {p.name: 0 for p in self.active_players}

        self._collect_blinds()

        for player in self.active_players:
            player.hand = self.deck.deal(5)
        self.log.append("Rozdano karty.")

        self.game_phase = 'betting1'
        self.current_player_idx = 2 % len(self.active_players)
        self.last_raiser = self.active_players[1 % len(self.active_players)]

        self._advance_game_to_next_action()

    def process_human_action(self, action: str, amount: int = 0):
        """Przetwarza akcję wykonaną przez gracza-człowieka."""
        if self.is_waiting_for_human():
            player = self.active_players[self.current_player_idx]
            self._process_player_action(player, action, amount)
            self._advance_game_to_next_action()
        else:
            self.log.append(f"Błąd: Próba akcji poza turą gracza.")

    def process_human_exchange(self, card_indices: list):
        """Przetwarza wymianę kart dla gracza-człowieka."""
        if self.game_phase == 'exchange' and self.is_waiting_for_human():
            player = self.active_players[self.current_player_idx]
            self._exchange_cards_for_player(player, card_indices)
            self._advance_game_to_next_action()
        else:
            self.log.append(f"Błąd: Próba wymiany kart w nieodpowiedniej fazie.")

    def get_game_state(self) -> dict:
        human_player = next((p for p in self.all_players if not isinstance(p, BotPlayer)), None)

        current_player = None
        if self.game_phase not in ['round-over', 'game-over'] and self.current_player_idx < len(self.active_players):
            current_player = self.active_players[self.current_player_idx]

        player_bet = self.bets_this_round.get(current_player.name, 0) if current_player else 0
        amount_to_call = self.current_bet_to_call - player_bet

        return {
            "pot": self.pot,
            "log": self.log.copy(),
            "game_phase": self.game_phase,
            "is_waiting_for_human": self.is_waiting_for_human(),
            "amount_to_call": amount_to_call,
            "min_raise": self.current_bet_to_call + self.min_raise_amount,
            "human_player": {
                "name": human_player.name,
                "hand_str": human_player.cards_to_str(),
                "hand_list": human_player.hand,
                "stack": human_player.get_stack_amount(),
            } if human_player else None,
            "opponents": [
                {"name": p.name, "stack": p.get_stack_amount(), "is_active": p in self.active_players}
                for p in self.all_players if p != human_player
            ]
        }

    # --- Prywatne metody pomocnicze ---

    def _collect_blinds(self):
        sb_player = self.active_players[0 % len(self.active_players)]
        bb_player = self.active_players[1 % len(self.active_players)]

        sb_amount = min(self.small_blind, sb_player.stack)
        sb_player.bet(sb_amount)
        self.pot += sb_amount
        self.bets_this_round[sb_player.name] = sb_amount
        self.log.append(f"{sb_player.name} płaci small blind: {sb_amount}")

        bb_amount = min(self.big_blind, bb_player.stack)
        bb_player.bet(bb_amount)
        self.pot += bb_amount
        self.bets_this_round[bb_player.name] = bb_amount
        self.log.append(f"{bb_player.name} płaci big blind: {bb_amount}")

        self.current_bet_to_call = self.big_blind
        self.min_raise_amount = self.big_blind

    def _advance_game_to_next_action(self):
        if len(self.active_players) <= 1:
            return self._end_round()

        while True:
            if self.game_phase in ['betting1', 'betting2'] and self._is_betting_over():
                self._move_to_next_phase()
                if len(self.active_players) <= 1:
                    return self._end_round()
                continue

            if self.game_phase == 'exchange' and self._is_exchange_over():
                self._move_to_next_phase()
                continue

            if self.game_phase in ['round-over', 'game-over']:
                break

            current_player = self.active_players[self.current_player_idx]

            if not isinstance(current_player, BotPlayer):
                self.log.append(f"Twoja tura, {current_player.name}.")
                break

            if self.game_phase in ['betting1', 'betting2']:
                player_bet = self.bets_this_round.get(current_player.name, 0)
                amount_to_call = self.current_bet_to_call - player_bet

                action, amount = current_player.get_bet_action(
                    self.hand_value(current_player.get_player_hand()),
                    amount_to_call,
                    self.pot,
                    self.min_raise_amount,
                    current_player.stack,
                    self.small_blind
                )
                self._process_player_action(current_player, action, amount)
            elif self.game_phase == 'exchange':
                indices = current_player.get_exchange_decision(
                    current_player.hand,
                    self.hand_value(current_player.get_player_hand())
                )
                self._exchange_cards_for_player(current_player, indices)

    def _process_player_action(self, player, action, amount):
        player_bet_this_round = self.bets_this_round.get(player.name, 0)
        amount_to_call = self.current_bet_to_call - player_bet_this_round

        if action == 'fold':
            self.log.append(f"{player.name} pasuje.")
            self.active_players.pop(self.current_player_idx)
            if self.current_player_idx >= len(self.active_players):
                self.current_player_idx = 0

        elif action == 'check':
            if amount_to_call > 0:
                self.log.append(f"{player.name} nie mógł czekać, pasuje.")
                self.active_players.pop(self.current_player_idx)
                if self.current_player_idx >= len(self.active_players):
                    self.current_player_idx = 0
            else:
                self.log.append(f"{player.name} czeka.")
                self.current_player_idx = (self.current_player_idx + 1) % len(self.active_players)

        elif action == 'call':
            call_amount = min(amount_to_call, player.stack)
            player.bet(call_amount)
            self.pot += call_amount
            self.bets_this_round[player.name] += call_amount
            self.log.append(f"{player.name} wyrównuje, dokładając {call_amount}.")
            if player.stack == 0:
                self.log.append(f"{player.name} jest all-in!")
            self.current_player_idx = (self.current_player_idx + 1) % len(self.active_players)

        elif action == 'raise':
            total_bet_for_round = amount
            raise_amount = total_bet_for_round - player_bet_this_round

            is_valid_raise = True
            if raise_amount > player.stack:
                self.log.append(f"{player.name}: Błędne podbicie - za mało żetonów. Zmieniono na all-in.")
                raise_amount = player.stack
                total_bet_for_round = player_bet_this_round + raise_amount

            min_allowed_total_bet = self.current_bet_to_call + self.min_raise_amount
            if total_bet_for_round < min_allowed_total_bet and player.stack >= min_allowed_total_bet - player_bet_this_round:
                self.log.append(f"{player.name}: Błędne podbicie - za niska kwota. Zmieniono na call.")
                call_amount = min(amount_to_call, player.stack)
                player.bet(call_amount)
                self.pot += call_amount
                self.bets_this_round[player.name] += call_amount
                is_valid_raise = False

            if is_valid_raise:
                player.bet(raise_amount)
                self.pot += raise_amount

                new_raise_delta = total_bet_for_round - self.current_bet_to_call
                self.min_raise_amount = max(self.min_raise_amount, new_raise_delta)
                self.current_bet_to_call = total_bet_for_round
                self.bets_this_round[player.name] = total_bet_for_round
                self.last_raiser = player
                self.log.append(f"{player.name} podbija do {total_bet_for_round}.")
                if player.stack == 0:
                    self.log.append(f"{player.name} jest all-in!")

            self.current_player_idx = (self.current_player_idx + 1) % len(self.active_players)

    def _exchange_cards_for_player(self, player, indices_to_exchange):
        """Logika wymiany kart dla jednego gracza."""
        num_to_exchange = len(indices_to_exchange)
        if num_to_exchange > 0:
            cards_to_discard = [player.hand[i] for i in sorted(indices_to_exchange, reverse=True)]
            for card in cards_to_discard:
                player.hand.remove(card)
                self.deck.discard_to_bottom(card)

            new_cards = self.deck.deal(num_to_exchange)
            player.hand.extend(new_cards)
            self.log.append(f"{player.name} wymienia {num_to_exchange} kart.")
        else:
            self.log.append(f"{player.name} nie wymienia kart.")

        player.has_exchanged = True
        self.current_player_idx = (self.current_player_idx + 1) % len(self.active_players)

    def _is_betting_over(self):
        """Sprawdza, czy runda licytacji dobiegła końca."""
        if len(self.active_players) <= 1:
            return True

        if self.active_players[self.current_player_idx] == self.last_raiser:
            return True

        max_bet = self.current_bet_to_call
        for p in self.active_players:
            if p.stack > 0 and self.bets_this_round.get(p.name, 0) != max_bet:
                return False

        return True

    def _is_exchange_over(self):
        """Sprawdza, czy wszyscy aktywni gracze dokonali wymiany."""
        return all(hasattr(p, 'has_exchanged') and p.has_exchanged for p in self.active_players)

    def _move_to_next_phase(self):
        """Przesuwa grę do następnej fazy (np. z licytacji do wymiany)."""
        if self.game_phase == 'betting1':
            self.game_phase = 'exchange'
            self.log.append("--- Faza Wymiany ---")
            for p in self.active_players:
                p.has_exchanged = False
            self.current_player_idx = 0

        elif self.game_phase == 'exchange':
            self.game_phase = 'betting2'
            self.log.append("--- Druga Runda Licytacji ---")
            self.current_bet_to_call = 0
            self.min_raise_amount = self.big_blind
            self.bets_this_round = {p.name: 0 for p in self.active_players}
            self.current_player_idx = 0
            self.last_raiser = None

        elif self.game_phase == 'betting2':
            self._end_round()

    def _end_round(self):
        """Kończy rundę, przechodząc do showdownu i przyznania puli."""
        self.game_phase = 'showdown'
        self.log.append("--- Showdown ---")

        if len(self.active_players) == 1:
            winner = self.active_players[0]
            self.log.append(f"Wszyscy inni spasowali. Wygrywa {winner.name}.")
            winners = [winner]
        else:
            best_hand_value = (-1, [])
            winners = []
            for player in self.active_players:
                strength, kickers, name = self.hand_value(player.get_player_hand())
                self.log.append(f"{player.name} ma: {player.cards_to_str()} ({name})")

                if not winners or strength > best_hand_value[0]:
                    best_hand_value = (strength, kickers)
                    winners = [player]
                elif strength == best_hand_value[0]:
                    if kickers > best_hand_value[1]:
                        best_hand_value = (strength, kickers)
                        winners = [player]
                    elif kickers == best_hand_value[1]:
                        winners.append(player)

            winner_names = ", ".join([w.name for w in winners])
            self.log.append(f"Najlepsza ręka: {name}. Wygrywa: {winner_names}")

        # Podział puli
        pot_per_winner = self.pot // len(winners)
        for winner in winners:
            winner.win_pot(pot_per_winner)
            self.log.append(f"{winner.name} wygrywa {pot_per_winner} żetonów.")

        # Reszta z dzielenia (jeśli jest) trafia do pierwszego zwycięzcy
        remainder = self.pot % len(winners)
        if remainder > 0 and winners:
            winners[0].win_pot(remainder)
            self.log.append(f"{winners[0].name} dodatkowo otrzymuje {remainder} żetonów z reszty.")

        self.pot = 0
        self.game_phase = 'round-over'

    def is_waiting_for_human(self) -> bool:
        if self.game_phase in ['round-over', 'game-over']:
            return False
        if self.current_player_idx >= len(self.active_players):
            return False  # Indeks poza zakresem

        current_player = self.active_players[self.current_player_idx]
        return not isinstance(current_player, BotPlayer)

    def hand_value(self, hand_tuple):
        if not hand_tuple or not all(isinstance(c, Card) for c in hand_tuple) or len(hand_tuple) != 5:
            return (-1, [], "Invalid Hand")

        hand = list(hand_tuple)
        value_map = Card.value_order

        values = sorted([card.value() for card in hand], reverse=True)
        ranks = sorted([card.rank for card in hand], key=lambda r: value_map[r], reverse=True)
        suits = [card.suit for card in hand]

        counts = {rank: ranks.count(rank) for rank in set(ranks)}
        sorted_counts = sorted(counts.items(), key=lambda item: (-item[1], -value_map[item[0]]))

        is_flush = len(set(suits)) == 1
        is_straight = False
        unique_values_for_straight_check = sorted(list(set(values)), reverse=True)

        if len(unique_values_for_straight_check) == 5:
            if unique_values_for_straight_check[0] - unique_values_for_straight_check[4] == 4:
                is_straight = True
            elif set(ranks) == {'A', '5', '4', '3', '2'}:
                is_straight = True
                values = [value_map['5'], value_map['4'], value_map['3'], value_map['2'], value_map['A']]

        if is_straight and is_flush:
            return (9, values, "Poker")
        if sorted_counts[0][1] == 4:
            kicker = [value_map[r] for r in ranks if r != sorted_counts[0][0]]
            return (8, [value_map[sorted_counts[0][0]]] + kicker, "Kareta")
        if sorted_counts[0][1] == 3 and sorted_counts[1][1] == 2:
            return (7, [value_map[sorted_counts[0][0]], value_map[sorted_counts[1][0]]], "Full")
        if is_flush:
            return (6, values, "Kolor")
        if is_straight:
            return (5, values, "Strit")
        if sorted_counts[0][1] == 3:
            kickers = sorted([value_map[r] for r in ranks if r != sorted_counts[0][0]], reverse=True)
            return (4, [value_map[sorted_counts[0][0]]] + kickers, "Trójka")
        if sorted_counts[0][1] == 2 and sorted_counts[1][1] == 2:
            kicker = [value_map[r] for r in ranks if r != sorted_counts[0][0] and r != sorted_counts[1][0]]
            pairs = sorted([value_map[sorted_counts[0][0]], value_map[sorted_counts[1][0]]], reverse=True)
            return (3, pairs + kicker, "Dwie pary")
        if sorted_counts[0][1] == 2:
            kickers = sorted([value_map[r] for r in ranks if r != sorted_counts[0][0]], reverse=True)
            return (2, [value_map[sorted_counts[0][0]]] + kickers, "Para")

        return (1, values, "Wysoka karta")
