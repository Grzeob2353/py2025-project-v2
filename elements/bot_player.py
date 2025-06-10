import random
from .Player import Player
from .Card import Card


class BotPlayer(Player):
    def __init__(self, money, name="Bot", bot_difficulty="random"):
        super().__init__(money, name)
        self.is_bot = True
        self.bot_difficulty = bot_difficulty

    def get_bet_action(self, current_hand_strength_tuple, current_bet_to_call, pot_size, min_raise_amount, stack_amount,
                       small_blind_value):
        available_actions_choices = []

        can_fold = True
        can_check = current_bet_to_call == 0
        can_call = stack_amount >= current_bet_to_call if current_bet_to_call > 0 else False  # Może callować tylko jeśli jest co callować
        if current_bet_to_call > 0 and stack_amount > 0 and stack_amount < current_bet_to_call:  # Może wejść all-in by callować
            can_call = True

        min_total_bet_for_raise = current_bet_to_call + min_raise_amount
        if can_check:  # Jeśli można czekać, minimalny bet to min_raise_amount
            min_total_bet_for_raise = min_raise_amount

        can_raise = stack_amount >= min_total_bet_for_raise

        if can_fold:
            available_actions_choices.append("fold")
        if can_check:
            available_actions_choices.append("check")
        if can_call:
            available_actions_choices.append("call")
        if can_raise:
            available_actions_choices.append("raise")

        if not available_actions_choices:  # Sytuacja awaryjna, np. stack=0 i musi spasować
            return "fold", 0

        chosen_action = random.choice(available_actions_choices)

        final_raise_total_amount = 0

        if chosen_action == "raise":
            max_possible_total_bet = stack_amount  # Całkowita kwota, jaką bot może postawić (all-in)

            if min_total_bet_for_raise > max_possible_total_bet:  # Nie stać na minimalne podbicie
                # Jeśli nie może podbić, spróbuj sprawdzić lub spasować lub wyrównać
                if can_call:
                    chosen_action = "call"
                elif can_check:
                    chosen_action = "check"
                else:
                    chosen_action = "fold"
            else:
                final_raise_total_amount = random.randint(min_total_bet_for_raise, max_possible_total_bet)

        # Jeśli akcja to nie raise, kwota jest nieistotna dla tej funkcji (GameEngine ją obsłuży)
        if chosen_action != "raise":
            final_raise_total_amount = 0

        return chosen_action, final_raise_total_amount

    def get_exchange_decision(self, hand_as_displayed_objects, current_hand_strength_tuple):
        num_to_exchange = random.randint(0, len(hand_as_displayed_objects))  # Może wymienić od 0 do wszystkich 5 kart

        indices_to_exchange = []
        if num_to_exchange > 0:
            available_indices = list(range(len(hand_as_displayed_objects)))
            indices_to_exchange = random.sample(available_indices, num_to_exchange)

        return indices_to_exchange