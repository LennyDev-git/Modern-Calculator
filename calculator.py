import tkinter as tk
from tkinter import font

# Hauptfenster
root = tk.Tk()
root.title("Calculator")
root.geometry("400x600")
root.resizable(False, False)
root.configure(bg="#1E1E1E")  # Dunkler Hintergrund

# Schriftarten
display_font = font.Font(family="Helvetica", size=32, weight="bold")
button_font = font.Font(family="Helvetica", size=18, weight="bold")

# Display
display = tk.Entry(root, font=display_font, bg="#1E1E1E", fg="white", bd=0, justify="right")
display.pack(expand=True, fill="both", padx=10, pady=(20, 10))

# Rahmen für Buttons
btn_frame = tk.Frame(root, bg="#1E1E1E")
btn_frame.pack(expand=True, fill="both")

# Button-Farben
num_bg = "#2D2D2D"       # Dunkelgrau für Zahlen
num_fg = "white"
op_bg = "#1E90FF"        # Hellblau für Operatoren
op_fg = "white"
del_bg = "#FF3B30"       # Rot für C
del_fg = "white"
hover_bg = "#505050"

# Funktionen
def add_to_display(value):
    display.insert(tk.END, value)

def clear_display():
    display.delete(0, tk.END)

def calculate():
    try:
        result = eval(display.get())
        display.delete(0, tk.END)
        display.insert(tk.END, str(result))
    except:
        display.delete(0, tk.END)
        display.insert(tk.END, "Error")

# Button Layout
buttons = [
    ["C", "(", ")", "/"],
    ["7", "8", "9", "*"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "=", ""]
]

# Buttons erstellen
for r, row in enumerate(buttons):
    for c, char in enumerate(row):
        if char == "":
            continue
        if char in "+-*/=":
            bg = op_bg
            fg = op_fg
        elif char == "C":
            bg = del_bg
            fg = del_fg
        else:
            bg = num_bg
            fg = num_fg

        btn = tk.Button(btn_frame, text=char, bg=bg, fg=fg, font=button_font,
                        border=0, relief="ridge", activebackground=hover_bg)
        btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

        # Button-Funktion zuweisen
        if char == "C":
            btn.config(command=clear_display)
        elif char == "=":
            btn.config(command=calculate)
        else:
            btn.config(command=lambda ch=char: add_to_display(ch))

# Zeilen & Spalten anpassen
for i in range(5):
    btn_frame.rowconfigure(i, weight=1)
for i in range(4):
    btn_frame.columnconfigure(i, weight=1)

root.mainloop()



