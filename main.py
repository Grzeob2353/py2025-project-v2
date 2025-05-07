from elements.Player import Player
from elements.Deck import Deck
from elements.game_engine import GameEngine

def setup_game():
    num_players = int(input("Ilu graczy bierze udział? "))
    players = []
    for i in range(num_players):
        name = input(f"Podaj imię gracza {i + 1}: ")
        players.append(Player(200, name))

    deck = Deck()
    return GameEngine(players, deck)

if __name__ == "__main__":
    engine = setup_game()
    engine.play_round()