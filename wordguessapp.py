# main.py

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
import os
import json
import random

JSON_FILE = "words.json"
SCORE_FILE = "score.json"
HISTORY_FILE = "history.json"


class WordManagerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding=20, spacing=10)

        self.word_input = MDTextField(hint_text="Enter Word", mode="rectangle")
        self.difficulty_input = MDTextField(hint_text="Enter Difficulty (Easy/Medium/Hard)", mode="rectangle")
        self.hint_input = MDTextField(hint_text="Enter Hint", mode="rectangle")

        self.add_button = MDRaisedButton(text="Add Word", on_release=self.add_word)
        self.go_to_game = MDRaisedButton(text="Go to Game", on_release=lambda x: setattr(self.manager, 'current', 'game'))

        self.word_list_label = MDLabel(text="Word List Preview", halign="center")

        self.scroll = MDScrollView()
        self.scroll_layout = MDBoxLayout(orientation="vertical", size_hint_y=None)
        self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))
        self.scroll.add_widget(self.scroll_layout)

        self.layout.add_widget(MDLabel(text="Word Manager", halign="center", font_style="H5"))
        for widget in [self.word_input, self.difficulty_input, self.hint_input,
                       self.add_button, self.word_list_label, self.scroll, self.go_to_game]:
            self.layout.add_widget(widget)

        self.add_widget(self.layout)
        self.update_word_list()

    def load_data(self):
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_data(self, data):
        with open(JSON_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def update_word_list(self):
        data = self.load_data()
        self.scroll_layout.clear_widgets()
        if not data:
            self.word_list_label.text = "No words added."
        else:
            self.word_list_label.text = "Word List Preview"
            for i, item in enumerate(data[-20:]):
                label = MDLabel(
                    text=f"{i+1}. {item['word']} - {item['difficulty']}",
                    halign="left",
                    size_hint_y=None,
                    height=30
                )
                self.scroll_layout.add_widget(label)

    def add_word(self, instance):
        word = self.word_input.text.strip()
        difficulty = self.difficulty_input.text.strip()
        hint = self.hint_input.text.strip()

        if word and difficulty and hint:
            try:
                data = self.load_data()
                data.append({"word": word, "difficulty": difficulty, "hint": hint})
                self.save_data(data)

                Snackbar(text=f"Added '{word}'").open()
                self.word_input.text = self.difficulty_input.text = self.hint_input.text = ""
                self.update_word_list()
            except Exception as e:
                Snackbar(text=f"Error adding word: {str(e)}").open()
        else:
            Snackbar(text="All fields are required").open()


class WordGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer = 60
        self.score = 0
        self.high_score = self.load_high_score()
        self.clock_event = None
        self.words = []
        self.used_indices = set()

        self.layout = MDBoxLayout(orientation='vertical', padding=20, spacing=10)

        self.title = MDLabel(text="Word Guess Game", halign="center", font_style="H5")
        self.scrambled_label = MDLabel(text="Word", halign="center")
        self.timer_label = MDLabel(text="60s", halign="center")
        self.score_label = MDLabel(text="Score: 0 | High Score: 0", halign="center")
        self.entry = MDTextField(hint_text="Your Guess", mode="rectangle")
        self.check_button = MDRaisedButton(text="Check", on_release=self.check_answer)
        self.hint_button = MDRaisedButton(text="Hint", on_release=self.show_hint)
        self.next_button = MDRaisedButton(text="Next Word", on_release=self.next_word)
        self.back_button = MDRaisedButton(text="Back to Manager", on_release=self.switch_to_manager)

        self.hint_label = MDLabel(text="", halign="center")
        self.result_label = MDLabel(text="", halign="center")

        # Scrollable history
        self.history_label = MDLabel(text="Guess History", halign="center")
        self.history_scroll = MDScrollView(size_hint=(1, 0.3))
        self.history_layout = MDBoxLayout(orientation="vertical", size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        self.history_scroll.add_widget(self.history_layout)

        widgets = [
            self.title, self.scrambled_label, self.timer_label, self.score_label,
            self.entry, self.check_button, self.hint_button, self.next_button,
            self.hint_label, self.result_label, self.history_label, self.history_scroll,
            self.back_button
        ]

        for w in widgets:
            self.layout.add_widget(w)

        self.add_widget(self.layout)
        self.load_words()
        self.load_history()
        self.next_word()

    def load_words(self):
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r") as f:
                    self.words = json.load(f)
            except json.JSONDecodeError:
                self.words = []
        if not self.words:
            self.words = [{"word": "example", "difficulty": "Medium", "hint": "A sample word"}]
        self.used_indices = set()

    def get_random_word(self):
        if len(self.used_indices) == len(self.words):
            self.used_indices.clear()
        while True:
            index = random.randint(0, len(self.words) - 1)
            if index not in self.used_indices:
                self.used_indices.add(index)
                return self.words[index]

    def next_word(self, *args):
        self.stop_timer()
        word_data = self.get_random_word()
        self.current_word = word_data["word"]
        self.current_hint = word_data["hint"]
        self.current_difficulty = word_data["difficulty"]

        while True:
            scrambled = ''.join(random.sample(self.current_word, len(self.current_word)))
            if scrambled.lower() != self.current_word.lower():
                break

        self.scrambled_label.text = f"Guess: {scrambled}"
        self.timer = 60
        self.timer_label.text = "60s"
        self.entry.text = ""
        self.hint_label.text = ""
        self.result_label.text = ""
        self.start_timer()

    def check_answer(self, *args):
        guess = self.entry.text.strip().lower()
        correct = guess == self.current_word.lower()
        if correct:
            self.result_label.text = "Correct!"
            self.stop_timer()
            self.update_score(10 if self.current_difficulty.lower() == "easy" else 20)
        else:
            self.result_label.text = "Try Again"
        self.update_score_display()
        self.save_history(guess, correct)

    def show_hint(self, *args):
        self.hint_label.text = f"Hint: {self.current_hint}"
        if self.current_difficulty.lower() == "easy":
            self.update_score(-5)
            Snackbar(text="Hint penalty: -5 points for Easy").open()
            self.update_score_display()

    def update_score(self, points):
        self.score += points
        if self.score < 0:
            self.score = 0
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def update_score_display(self):
        self.score_label.text = f"Score: {self.score} | High Score: {self.high_score}"

    def load_high_score(self):
        if os.path.exists(SCORE_FILE):
            try:
                with open(SCORE_FILE, "r") as f:
                    return json.load(f).get("high_score", 0)
            except json.JSONDecodeError:
                return 0
        return 0

    def save_high_score(self):
        with open(SCORE_FILE, "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def start_timer(self):
        self.stop_timer()
        self.clock_event = Clock.schedule_interval(self.update_timer, 1)

    def stop_timer(self):
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None

    def update_timer(self, dt):
        self.timer -= 1
        self.timer_label.text = f"{self.timer}s"
        if self.timer <= 0:
            self.result_label.text = f"Time's up! Word was: {self.current_word}"
            self.stop_timer()

    def switch_to_manager(self, *args):
        self.stop_timer()
        self.manager.current = 'manager'

    def save_history(self, guess, correct):
        record = {
            "word": self.current_word,
            "guess": guess,
            "result": "Correct" if correct else "Wrong",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    history = json.load(f)
            except:
                pass
        history.append(record)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history[-30:], f, indent=4)  # Keep last 30
        self.load_history()

    def load_history(self):
        self.history_layout.clear_widgets()
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    history = json.load(f)
                for item in reversed(history):
                    lbl = MDLabel(
                        text=f"{item['time']} | {item['guess']} -> {item['result']} ({item['word']})",
                        size_hint_y=None, height=30
                    )
                    self.history_layout.add_widget(lbl)
            except:
                pass


class WordGuessGameApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(WordGameScreen(name='game'))
        sm.add_widget(WordManagerScreen(name='manager'))
        return sm


if __name__ == '__main__':
    WordGuessGameApp().run()
