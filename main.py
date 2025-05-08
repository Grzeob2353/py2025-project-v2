from elements.Player import Player
from elements.Deck import Deck
from elements.game_engine import GameEngine

def main():
    # Pobierz liczbę graczy
    while True:
        try:
            num_players = int(input("Podaj liczbę graczy (2–6): "))
            if 2 <= num_players <= 6:
                break
            print("Liczba graczy musi być z przedziału 2–6.")
        except ValueError:
            print("Wprowadź poprawną liczbę.")

    # Utwórz graczy
    players = []
    for i in range(num_players):
        name = input(f"Podaj nazwę gracza {i + 1}: ")
        players.append(Player(200, name))  # każdy zaczyna z 200 żetonami

    round_number = 1

    while True:
        print(f"\n=== Runda {round_number} ===")
        active_players = [p for p in players if p.stack > 0]

        if len(active_players) < 2:
            winner = active_players[0] if active_players else None
            if winner:
                print(f"Koniec gry! Zwycięzca: {winner.name} z {winner.stack} żetonami.")
            else:
                print("Wszyscy gracze odpadli.")
            break

        # Nowa talia na każdą rundę
        deck = Deck()
        engine = GameEngine(active_players, deck)
        engine.play_round()
        round_number += 1

        cont = input("Naciśnij Enter, aby kontynuować, lub wpisz cokolwiek, aby zakończyć: ")
        if cont.strip():
            break

if __name__ == "__main__":
    main()