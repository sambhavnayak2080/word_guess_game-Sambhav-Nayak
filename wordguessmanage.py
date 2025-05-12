import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

FILE_PATH = "words.json"

def load_data():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    with open(FILE_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def refresh_word_list():
    word_listbox.delete(0, tk.END)
    for entry in data:
        word_listbox.insert(tk.END, entry['word'])

def add_word():
    word = word_entry.get().strip().lower()
    hint = hint_entry.get().strip()
    difficulty = difficulty_var.get()

    if not word or not hint or not difficulty:
        messagebox.showwarning("Incomplete", "Please fill all fields.")
        return

    for entry in data:
        if entry['word'] == word:
            messagebox.showwarning("Duplicate", f"The word '{word}' already exists.")
            return

    data.append({"word": word, "hint": hint, "difficulty": difficulty})
    save_data(data)
    refresh_word_list()
    clear_inputs()
    messagebox.showinfo("Success", f"Word '{word}' added!")

def delete_word():
    selected = word_listbox.curselection()
    if not selected:
        messagebox.showwarning("Select", "Please select a word to delete.")
        return
    index = selected[0]
    word = data[index]['word']
    if messagebox.askyesno("Confirm", f"Delete word '{word}'?"):
        del data[index]
        save_data(data)
        refresh_word_list()
        clear_inputs()

def edit_word():
    selected = word_listbox.curselection()
    if not selected:
        messagebox.showwarning("Select", "Select a word to edit.")
        return

    index = selected[0]
    word = word_entry.get().strip().lower()
    hint = hint_entry.get().strip()
    difficulty = difficulty_var.get()

    if not word or not hint or not difficulty:
        messagebox.showwarning("Incomplete", "Please fill all fields.")
        return

    data[index] = {"word": word, "hint": hint, "difficulty": difficulty}
    save_data(data)
    refresh_word_list()
    clear_inputs()
    messagebox.showinfo("Updated", f"Word '{word}' updated successfully.")

def on_select(event):
    selected = word_listbox.curselection()
    if not selected:
        return
    index = selected[0]
    entry = data[index]
    word_entry.delete(0, tk.END)
    word_entry.insert(0, entry['word'])
    hint_entry.delete(0, tk.END)
    hint_entry.insert(0, entry['hint'])
    difficulty_var.set(entry['difficulty'])

def clear_inputs():
    word_entry.delete(0, tk.END)
    hint_entry.delete(0, tk.END)
    difficulty_var.set("easy")
    word_listbox.selection_clear(0, tk.END)

# Load data initially
data = load_data()

# GUI setup
root = tk.Tk()
root.title("Word Bank JSON Manager")
root.geometry("600x400")
root.configure(bg="#1f1f1f")

# Title
tk.Label(root, text="Word Bank Manager", font=("Arial", 18, "bold"), fg="white", bg="#1f1f1f").pack(pady=10)

# Entry fields
form_frame = tk.Frame(root, bg="#1f1f1f")
form_frame.pack(pady=10)

tk.Label(form_frame, text="Word:", bg="#1f1f1f", fg="white").grid(row=0, column=0, sticky="e")
word_entry = tk.Entry(form_frame, width=30)
word_entry.grid(row=0, column=1, padx=5)

tk.Label(form_frame, text="Hint:", bg="#1f1f1f", fg="white").grid(row=1, column=0, sticky="e")
hint_entry = tk.Entry(form_frame, width=30)
hint_entry.grid(row=1, column=1, padx=5)

tk.Label(form_frame, text="Difficulty:", bg="#1f1f1f", fg="white").grid(row=2, column=0, sticky="e")
difficulty_var = tk.StringVar(value="easy")
difficulty_menu = ttk.Combobox(form_frame, textvariable=difficulty_var, values=["easy", "medium", "hard"], state="readonly")
difficulty_menu.grid(row=2, column=1)

# Buttons
btn_frame = tk.Frame(root, bg="#1f1f1f")
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="Add", command=add_word).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Edit", command=edit_word).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="Delete", command=delete_word).grid(row=0, column=2, padx=5)
ttk.Button(btn_frame, text="Clear", command=clear_inputs).grid(row=0, column=3, padx=5)

# Listbox
list_frame = tk.Frame(root, bg="#1f1f1f")
list_frame.pack(pady=10)

word_listbox = tk.Listbox(list_frame, height=10, width=50)
word_listbox.pack()
word_listbox.bind("<<ListboxSelect>>", on_select)

# Load list
refresh_word_list()

root.mainloop()
