import json
import os
from datetime import datetime


class SessionManager:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            try:
                os.makedirs(self.data_dir)
            except OSError as e:
                print(f"Błąd tworzenia katalogu {self.data_dir}: {e}")
                raise

    def save_session(self, session_data: dict) -> None:
        if 'game_id' not in session_data:
            print("Błąd: Klucz 'game_id' jest wymagany w danych sesji.")
            return

        game_id = session_data['game_id']
        file_path = os.path.join(self.data_dir, f"session_{game_id}.jsonl")

        try:
            with open(file_path, 'a') as f:
                json.dump(session_data, f)
                f.write('\n')
        except IOError as e:
            print(f"Błąd zapisu do pliku {file_path}: {e}")
            raise
        except TypeError as e:
            print(f"Błąd serializacji danych sesji do JSON: {e}")
            raise

    def load_session(self, game_id: str) -> dict:
        file_path = os.path.join(self.data_dir, f"session_{game_id}.jsonl")

        if not os.path.exists(file_path):
            print(f"Plik sesji {file_path} nie istnieje.")
            return {}

        rounds_history = []
        last_round_state = {}

        try:
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        round_data = json.loads(line.strip())
                        rounds_history.append(round_data)
                    except json.JSONDecodeError as e:
                        print(f"Błąd dekodowania JSON w linii pliku {file_path}: {line.strip()}. Błąd: {e}")
                        continue

            if rounds_history:
                last_round_state = rounds_history[-1]

                game_state_to_resume = {
                    'game_id': game_id,
                    'players': last_round_state.get('players_final_state', []),
                    'rounds_played_count': len(rounds_history),
                    'history': rounds_history
                }
                return game_state_to_resume
            else:
                return {}

        except IOError as e:
            print(f"Błąd odczytu pliku {file_path}: {e}")
            raise
        except Exception as e:
            print(f"Niespodziewany błąd podczas ładowania sesji {game_id}: {e}")
            raise
        return {}

    def save_config(self, config_data: dict, config_file_name: str = "config.json") -> None:
        file_path = os.path.join(".", config_file_name)
        try:
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=4)
        except IOError as e:
            print(f"Błąd zapisu konfiguracji do pliku {file_path}: {e}")
            raise
        except TypeError as e:
            print(f"Błąd serializacji danych konfiguracji do JSON: {e}")
            raise

    def load_config(self, config_file_name: str = "config.json") -> dict:
        file_path = os.path.join(".", config_file_name)
        if not os.path.exists(file_path):
            print(f"Plik konfiguracyjny {file_path} nie istnieje.")
            return {}
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
                return config_data
        except IOError as e:
            print(f"Błąd odczytu konfiguracji z pliku {file_path}: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Błąd dekodowania JSON w pliku konfiguracyjnym {file_path}: {e}")
            return {}
        except Exception as e:
            print(f"Niespodziewany błąd podczas ładowania konfiguracji: {e}")
            raise
        return {}