import tkinter as tk
from tkinter import ttk, messagebox
import random
import json

def load_words(filepath='words.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

class WordGuessGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Word Guessing Game")
        self.master.geometry("550x450")
        self.words_data = load_words()

        # Dark mode colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#3a9efd"

        self.master.configure(bg=self.bg_color)

        # Stats and control
        self.wins = 0
        self.losses = 0
        self.difficulty = None
        self.timer_seconds = 60
        self.timer_id = None

        self.start_difficulty_selection()

    def start_difficulty_selection(self):
        self.clear_screen()

        self.style_label("Select Difficulty", size=18).pack(pady=20)
        self.difficulty_choice = tk.StringVar(value="easy")

        for level in ["easy", "medium", "hard"]:
            ttk.Radiobutton(
                self.master, text=level.capitalize(), value=level,
                variable=self.difficulty_choice
            ).pack(pady=5)

        self.style_button("Start Game", self.start_game).pack(pady=20)
        self.display_scoreboard()

    def start_game(self):
        self.difficulty = self.difficulty_choice.get()
        filtered_words = [entry for entry in self.words_data if entry['difficulty'] == self.difficulty]
        if not filtered_words:
            messagebox.showerror("No Words", f"No words for difficulty: {self.difficulty}")
            return

        word_entry = random.choice(filtered_words)
        self.word = word_entry['word']
        self.hint = word_entry['hint']
        self.guessed = set()
        self.attempts_left = 7
        self.timer_seconds = 60

        self.setup_game_screen()
        self.start_timer()

    def setup_game_screen(self):
        self.clear_screen()

        self.style_label("Hint:", size=13).pack(pady=5)
        self.hint_label = self.style_label("", wrap=450, fg=self.accent_color)
        self.hint_label.pack()
        self.animate_typing(self.hint, self.hint_label)

        self.word_display = tk.StringVar()
        self.update_display()
        tk.Label(self.master, textvariable=self.word_display,
                 font=("Courier", 24), bg=self.bg_color, fg=self.fg_color).pack(pady=15)

        self.entry = tk.Entry(self.master, font=("Arial", 14), bg="#2d2d2d", fg=self.fg_color, insertbackground="white")
        self.entry.pack()
        self.entry.bind("<Return>", self.make_guess)

        self.status_label = self.style_label(f"Attempts left: {self.attempts_left}", size=12)
        self.status_label.pack(pady=10)

        self.timer_label = self.style_label(f"Time left: {self.timer_seconds} s", size=12, fg="orange")
        self.timer_label.pack()

        self.style_button("Guess", self.make_guess).pack(pady=5)

        self.scoreboard_label = self.style_label("", size=12)
        self.scoreboard_label.pack(pady=5)
        self.update_scoreboard()

    def update_display(self):
        display_text = ' '.join([ch if ch in self.guessed else '_' for ch in self.word])
        self.word_display.set(display_text)

    def make_guess(self, event=None):
        guess = self.entry.get().lower()
        self.entry.delete(0, tk.END)

        if not guess.isalpha() or len(guess) != 1:
            messagebox.showwarning("Invalid Input", "Enter a single alphabet.")
            return

        if guess in self.guessed:
            messagebox.showinfo("Repeated", f"You already guessed '{guess}'.")
            return

        self.guessed.add(guess)

        if guess in self.word:
            self.update_display()
            if all(letter in self.guessed for letter in self.word):
                self.stop_timer()
                self.wins += 1
                self.end_game(win=True)
        else:
            self.attempts_left -= 1
            self.status_label.config(text=f"Attempts left: {self.attempts_left}")
            if self.attempts_left == 0:
                self.stop_timer()
                self.losses += 1
                self.end_game(win=False)

    def end_game(self, win):
        result_msg = f"You won! The word was '{self.word}'" if win else f"You lost! The word was '{self.word}'"
        messagebox.showinfo("Game Over", result_msg)
        self.show_post_game_screen()

    def show_post_game_screen(self):
        self.clear_screen()

        self.style_label("Game Over", size=18).pack(pady=15)
        self.result_label = self.style_label("", size=14)
        self.result_label.pack(pady=5)
        self.fade_in_text(f"The word was: {self.word}", self.result_label)

        self.style_button("Play Again", self.start_difficulty_selection).pack(pady=10)
        self.style_button("Exit", self.master.quit).pack()

        self.display_scoreboard()

    def display_scoreboard(self):
        self.style_label("Scoreboard", size=13).pack(pady=(20, 5))
        tk.Label(self.master, text=f"Wins: {self.wins}   Losses: {self.losses}",
                 bg=self.bg_color, fg=self.fg_color, font=("Arial", 12)).pack()

    def update_scoreboard(self):
        self.fade_in_text(f"Wins: {self.wins}   Losses: {self.losses}", self.scoreboard_label)

    def clear_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def animate_typing(self, text, label, idx=0):
        if idx <= len(text):
            label.config(text=text[:idx])
            self.master.after(30, lambda: self.animate_typing(text, label, idx + 1))

    def fade_in_text(self, full_text, label, current=0):
        if current <= len(full_text):
            label.config(text=full_text[:current])
            self.master.after(40, lambda: self.fade_in_text(full_text, label, current + 1))

    def style_label(self, text, size=12, fg=None, wrap=0):
        return tk.Label(self.master, text=text, font=("Arial", size),
                        bg=self.bg_color, fg=fg or self.fg_color, wraplength=wrap)

    def style_button(self, text, command):
        return ttk.Button(self.master, text=text, command=command)

    # Timer logic
    def start_timer(self):
        self.update_timer_label()
        self.timer_id = self.master.after(1000, self.countdown)

    def countdown(self):
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.update_timer_label()
            self.timer_id = self.master.after(1000, self.countdown)
        else:
            self.losses += 1
            self.stop_timer()
            self.end_game(win=False)

    def update_timer_label(self):
        self.timer_label.config(text=f"Time left: {self.timer_seconds} s")

    def stop_timer(self):
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

# Launch
if __name__ == "__main__":
    root = tk.Tk()
    app = WordGuessGame(root)
    root.mainloop()
