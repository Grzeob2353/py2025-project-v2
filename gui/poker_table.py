import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel


class PokerTable(tk.Tk):
    def __init__(self, game_logic_handler, title="Poker Game"):
        super().__init__()
        self.title(title)
        self.geometry("1024x768")
        self.configure(bg='#006400')

        self.game_logic = game_logic_handler

        self.status_frame = tk.Frame(self, bg='#004d00', padx=10, pady=5)
        self.status_frame.pack(side='top', fill='x')

        self.opponents_frame = tk.Frame(self, bg='#006400', pady=20)
        self.opponents_frame.pack(expand=True, fill='both')

        self.player_frame = tk.Frame(self, bg='#004d00', padx=10, pady=10)
        self.player_frame.pack(side='bottom', fill='x')

        self.status_label = tk.Label(self.status_frame, text="Witaj w grze!", font=("Arial", 14), bg='#004d00',
                                     fg='white')
        self.pot_label = tk.Label(self.status_frame, text="Pula: 0", font=("Arial", 14), bg='#004d00', fg='white')
        self.player_hand_label = tk.Label(self.player_frame, text="Karty:", font=("Courier", 18, "bold"), bg='#004d00',
                                          fg='white')
        self.player_stack_label = tk.Label(self.player_frame, text="Stack: 0", font=("Arial", 14), bg='#004d00',
                                           fg='white')

        self.status_label.pack(side='left')
        self.pot_label.pack(side='right')
        self.player_hand_label.pack(pady=5)
        self.player_stack_label.pack(pady=5)

        self.opponent_labels = {}
        self._create_action_buttons()

    def _create_action_buttons(self):

        action_area = tk.Frame(self.player_frame, bg='#004d00')
        action_area.pack(pady=10)

        self.fold_button = tk.Button(action_area, text="Fold", font=("Arial", 12),
                                     command=lambda: self.game_logic.on_player_action('fold'))
        self.check_button = tk.Button(action_area, text="Check", font=("Arial", 12),
                                      command=lambda: self.game_logic.on_player_action('check'))
        self.call_button = tk.Button(action_area, text="Call", font=("Arial", 12),
                                     command=lambda: self.game_logic.on_player_action('call'))
        self.raise_button = tk.Button(action_area, text="Raise", font=("Arial", 12), command=self._handle_raise)

        self.fold_button.pack(side='left', padx=10)
        self.check_button.pack(side='left', padx=10)
        self.call_button.pack(side='left', padx=10)
        self.raise_button.pack(side='left', padx=10)
        self.toggle_action_buttons(False)  # Domyślnie wyłączone

    def _handle_raise(self):
        amount = simpledialog.askinteger("Raise", "Podaj całkowitą kwotę zakładu:", parent=self, minvalue=1)
        if amount:
            self.game_logic.on_player_action('raise', amount=amount)

    def toggle_action_buttons(self, is_enabled):
        state = 'normal' if is_enabled else 'disabled'
        self.fold_button.config(state=state)
        self.check_button.config(state=state)
        self.call_button.config(state=state)
        self.raise_button.config(state=state)

    def update_view(self, game_state):
        self.pot_label.config(text=f"Pula: {game_state.get('pot', 0)}")
        self.status_label.config(text=game_state.get('status_message', ''))

        human_player = game_state.get('human_player')
        if human_player:
            self.player_hand_label.config(text=human_player.get('hand_str', ''))
            self.player_stack_label.config(text=f"Stack: {human_player.get('stack', 0)}")

        for name, label in self.opponent_labels.items():
            label.destroy()
        self.opponent_labels.clear()

        for opponent in game_state.get('opponents', []):
            label = tk.Label(self.opponents_frame,
                             text=f"{opponent['name']}\nStack: {opponent['stack']}\nStatus: {opponent.get('status', '')}",
                             bg='#004d00', fg='white', font=("Arial", 12), bd=2, relief='raised')
            label.pack(side='left', padx=20, pady=20, anchor='n')
            self.opponent_labels[opponent['name']] = label

        self.update()

    def ask_for_cards_to_exchange(self, hand_size):
        indices_str = simpledialog.askstring("Wymiana Kart",
                                             "Podaj indeksy kart do wymiany (0-4, oddzielone spacją), lub zostaw puste:",
                                             parent=self)
        if indices_str is None:
            return []
        if not indices_str.strip():
            return []
        try:
            indices = [int(i) for i in indices_str.strip().split()]
            if any(idx < 0 or idx >= hand_size for idx in indices):
                messagebox.showwarning("Błąd", "Podałeś nieprawidłowy indeks.")
                return self.ask_for_cards_to_exchange(hand_size)
            return indices
        except ValueError:
            messagebox.showwarning("Błąd", "Podaj liczby oddzielone spacją.")
            return self.ask_for_cards_to_exchange(hand_size)

    def show_message(self, title, message):
        messagebox.showinfo(title, message, parent=self)