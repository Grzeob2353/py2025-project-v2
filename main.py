import time
from gui.poker_table import PokerTable
from elements.game_engine import GameEngine
from elements.Player import Player
from elements.bot_player import BotPlayer
from elements.Deck import Deck


class LocalGameController:
    def __init__(self):
        self.gui = PokerTable(self, "Lokalny Stół Pokera")

        players = [
            Player(money=1000, name="Ty"),
            BotPlayer(money=1000, name="Bot Ania"),
            BotPlayer(money=1000, name="Bot Bartek")
        ]

        self.engine = GameEngine(players, Deck())
        self.human_player_name = "Ty"

    def start_game(self):
        self.gui.after(500, self._start_new_round_flow)
        self.gui.mainloop()

    def _start_new_round_flow(self):
        self.engine.start_new_round()
        self.update_gui_from_engine()

        if self.engine.game_phase == 'game-over':
            self.gui.show_message("Koniec Gry", "Gra zakończona. Za mało graczy.")
            self.gui.destroy()
            return

        self.process_game_flow()

    def process_game_flow(self):
        if self.engine.is_waiting_for_human():
            self.gui.toggle_action_buttons(True)
            if self.engine.game_phase == 'exchange':
                self.handle_human_exchange()

        elif self.engine.game_phase == 'round-over':
            self.gui.show_message("Koniec Rundy", "\n".join(self.engine.log[-4:]))
            self.gui.after(2000, self._start_new_round_flow)

        elif self.engine.game_phase == 'game-over':
            self.gui.show_message("Koniec Gry", "Gra zakończona.")
            self.gui.destroy()
        else:
            self.update_gui_from_engine()

    def on_player_action(self, action: str, amount: int = 0):
        self.gui.toggle_action_buttons(False)
        self.engine.process_human_action(action, amount)
        self.update_gui_from_engine()
        self.gui.after(100, self.process_game_flow)

    def handle_human_exchange(self):
        self.gui.toggle_action_buttons(False)

        game_state = self.engine.get_game_state()
        hand_size = len(game_state['human_player']['hand_list'])

        indices = self.gui.ask_for_cards_to_exchange(hand_size)
        self.engine.process_human_exchange(indices)

        self.update_gui_from_engine()
        self.gui.after(100, self.process_game_flow)

    def update_gui_from_engine(self):
        game_state = self.engine.get_game_state()
        self.gui.update_view(game_state)


if __name__ == "__main__":
    game_controller = LocalGameController()
    game_controller.start_game()
