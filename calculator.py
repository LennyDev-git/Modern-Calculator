import tkinter as tk
from tkinter import font
import ast
import operator as op
import math
import re

# -------------------------
# Safe evaluator with math
# -------------------------
# Allowed binary/unary operators
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.UAdd: lambda x: +x,
    ast.USub: lambda x: -x,
}

# We'll provide allowed names (constants and functions). Some trig wrappers respect DEG_MODE.
DEG_MODE = False  # if True, trig functions interpret input as degrees

def sin_wrapper(x):
    return math.sin(math.radians(x)) if DEG_MODE else math.sin(x)
def cos_wrapper(x):
    return math.cos(math.radians(x)) if DEG_MODE else math.cos(x)
def tan_wrapper(x):
    return math.tan(math.radians(x)) if DEG_MODE else math.tan(x)
def asin_wrapper(x):
    r = math.asin(x)
    return math.degrees(r) if DEG_MODE else r
def acos_wrapper(x):
    r = math.acos(x)
    return math.degrees(r) if DEG_MODE else r
def atan_wrapper(x):
    r = math.atan(x)
    return math.degrees(r) if DEG_MODE else r

ALLOWED_NAMES = {
    # constants
    'pi': math.pi,
    'e': math.e,
    # basic math functions
    'sqrt': math.sqrt,
    'abs': abs,
    'floor': math.floor,
    'ceil': math.ceil,
    'round': round,
    # logs: ln and log10
    'ln': math.log,
    'log': math.log10,
    'log10': math.log10,
    # trig (wrappers)
    'sin': sin_wrapper,
    'cos': cos_wrapper,
    'tan': tan_wrapper,
    'asin': asin_wrapper,
    'acos': acos_wrapper,
    'atan': atan_wrapper,
    # others
    'pow': math.pow,
    'factorial': math.factorial,
}

# Preprocessing helpers (regex)
_re_percent = re.compile(r'(?P<num>\d+(\.\d+)?)[ ]*%')
_re_factorial = re.compile(r'(?P<num>\d+(\.\d+)?)!')
# implicit multiplication: number followed by ( or name (like 2pi -> 2*pi), or ) followed by number/name
_re_implicit_mul1 = re.compile(r'(\d)(\s*)(\()')          # 2( -> 2*(
_re_implicit_mul2 = re.compile(r'(\d)(\s*)([a-zA-Z])')    # 2pi -> 2*pi
_re_implicit_mul3 = re.compile(r'(\))(\s*)(\d)')         # )2 -> )*2
_re_implicit_mul4 = re.compile(r'(\))(\s*)([a-zA-Z(])')   # )sin -> )*sin, ) ( -> )*(

def preprocess_expression(expr: str) -> str:
    """
    Do safe preprocess:
     - convert ^ to **
     - convert percentages like 50% -> (50/100)
     - convert factorial n! -> factorial(n)
     - insert implicit multiplication where sensible
     - normalize unicode pi (π) etc.
    """
    # normalize whitespace
    expr = expr.strip()
    expr = expr.replace('×', '*').replace('·', '*').replace('−', '-')
    expr = expr.replace('π', 'pi')
    expr = expr.replace('^', '**')

    # % -> division by 100 (for immediate numbers). e.g. 50% -> (50/100)
    expr = _re_percent.sub(r'(\g<num>/100)', expr)

    # factorial: replace "5!" -> "factorial(5)"
    expr = _re_factorial.sub(lambda m: f"factorial({m.group('num')})", expr)

    # implicit multiplication: number followed by '(' or name, or ')' followed by number/name
    expr = _re_implicit_mul1.sub(r'\1*\3', expr)   # 2( -> 2*(
    expr = _re_implicit_mul2.sub(r'\1*\3', expr)   # 2pi -> 2*pi
    expr = _re_implicit_mul3.sub(r'\1*\3', expr)   # )2 -> )*2
    expr = _re_implicit_mul4.sub(r'\1*\3', expr)   # )sin -> )*sin or )(
    # remove accidental whitespace
    expr = re.sub(r'\s+', '', expr)
    return expr

def safe_eval(expression: str):
    """
    Evaluate a math expression safely using AST, allowing a whitelist
    of operators, constants and functions (ALLOWED_NAMES).
    """
    # Preprocess
    expression = preprocess_expression(expression)

    # Reject suspicious characters (only allow digits, operators, parens, letters, decimal point, comma)
    if re.search(r'[^0-9A-Za-z\.\+\-\*\/\%\^\(\)\!\,]', expression):
        # some allowed characters were normalized already; any other characters are rejected
        raise ValueError("Invalid characters in expression")

    try:
        node = ast.parse(expression, mode='eval')
    except Exception as e:
        raise ValueError("Syntax error") from e

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)

        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid constant")

        if isinstance(node, ast.Num):  # older ast node
            return node.n

        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                if op_type is ast.Div and right == 0:
                    raise ValueError("Division by zero")
                return ALLOWED_OPERATORS[op_type](left, right)
            raise ValueError("Operator not allowed")

        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[op_type](operand)
            raise ValueError("Unary operator not allowed")

        if isinstance(node, ast.Name):
            name = node.id
            if name in ALLOWED_NAMES:
                val = ALLOWED_NAMES[name]
                # constants are numbers; functions are callables
                if callable(val):
                    return val  # return function object for call handling in ast.Call
                return val
            raise ValueError(f"Name '{name}' is not allowed")

        if isinstance(node, ast.Call):
            # only allow simple name calls: sin(...), sqrt(...), factorial(...)
            func_node = node.func
            if not isinstance(func_node, ast.Name):
                raise ValueError("Only direct function calls allowed")
            fname = func_node.id
            if fname not in ALLOWED_NAMES:
                raise ValueError(f"Function '{fname}' not allowed")
            func = ALLOWED_NAMES[fname]
            # evaluate args
            args = [_eval(a) for a in node.args]
            # protect common errors (e.g., factorial non-int)
            try:
                return func(*args)
            except Exception as e:
                raise ValueError(f"Function call error: {e}") from e

        raise ValueError("Unsupported expression")

    return _eval(node)

# -------------------------
# GUI: standard + scientific
# -------------------------
root = tk.Tk()
root.title("Scientific Calculator")
root.geometry("520x700")
root.resizable(False, False)
root.configure(bg="#1E1E1E")

# Fonts
display_font = font.Font(family="Helvetica", size=28, weight="bold")
button_font = font.Font(family="Helvetica", size=14, weight="bold")
# <-- top-row buttons made a bit smaller
top_button_font = font.Font(family="Helvetica", size=15, weight="bold")
small_font = font.Font(family="Helvetica", size=10)

# Display
display_var = tk.StringVar()
display_entry = tk.Entry(root, textvariable=display_var, font=display_font,
                         bg="#1E1E1E", fg="white", bd=0, justify="right", insertbackground="white")
display_entry.pack(fill="x", padx=12, pady=(18, 6))
display_entry.focus_set()

# History
history_frame = tk.Frame(root, bg="#121212")
history_frame.pack(fill="x", padx=12, pady=(0, 8))
last_label = tk.Label(history_frame, text="History (last):", bg="#121212", fg="#A0A0A0", font=small_font, anchor="w")
last_label.pack(fill="x")
history_var = tk.StringVar(value=[])
history_listbox = tk.Listbox(history_frame, listvariable=history_var, height=4, bg="#121212", fg="white",
                             bd=0, highlightthickness=0, activestyle='none')
history_listbox.pack(fill="x")

# Button container frames
top_frame = tk.Frame(root, bg="#1E1E1E")
top_frame.pack(fill="both", expand=False, padx=10, pady=(0, 6))

btn_frame = tk.Frame(root, bg="#1E1E1E")
btn_frame.pack(expand=True, fill="both", padx=10, pady=10)

# Colors
NUM_BG = "#2D2D2D"
NUM_FG = "white"
OP_BG = "#1E90FF"
OP_FG = "white"
DEL_BG = "#FF3B30"
DEL_FG = "white"
EQUAL_BG = "#22C55E"
EQUAL_FG = "white"
SCI_BG = "#8B5CF6"
HOVER_BG = "#505050"

# state
MAX_DISPLAY_LEN = 80
history = []
scientific_mode = False
deg_mode = False  # degrees toggle

def set_deg_mode(val: bool):
    global DEG_MODE, deg_mode
    DEG_MODE = val
    deg_mode = val
    deg_btn.config(relief="sunken" if val else "raised")

def add_to_display(value: str):
    cur = display_var.get()
    if len(cur) + len(value) > MAX_DISPLAY_LEN:
        return
    display_var.set(cur + value)

def backspace():
    cur = display_var.get()
    if cur:
        display_var.set(cur[:-1])

def clear_display():
    display_var.set("")

def format_result(value):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if abs(value - round(value)) < 1e-12:
            return str(int(round(value)))
        return f"{value:.12g}"
    return str(value)

def evaluate_expression():
    expr = display_var.get().strip()
    if not expr:
        return
    try:
        result = safe_eval(expr)
        formatted = format_result(result)
        display_var.set(formatted)
        _add_history(expr, formatted)
    except Exception as e:
        display_var.set("Error")
        print("Eval error:", e)

def _add_history(expr, result):
    history.insert(0, f"{expr} = {result}")
    if len(history) > 12:
        history.pop()
    history_var.set(history)

# Button creation helper with hover
def make_button(parent, text, row, col, rowspan=1, colspan=1, bg=NUM_BG, fg=NUM_FG, command=None, font_to_use=None):
    use_font = font_to_use if font_to_use is not None else button_font
    btn = tk.Button(parent, text=text, bg=bg, fg=fg, font=use_font,
                    bd=0, relief="raised", activebackground=HOVER_BG, command=command)
    btn.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, sticky="nsew", padx=5, pady=5)
    def on_enter(e):
        btn['bg'] = HOVER_BG
    def on_leave(e):
        btn['bg'] = bg
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

# Standard layout (will be rebuilt if scientific toggle changes)
standard_buttons = [
    ["C", "(", ")", "⌫"],
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["+/-", "0", ".", "+"],
    ["%", "^", "=", ""]
]

# Scientific buttons to add when mode active
scientific_buttons = [
    ["sin", "cos", "tan", "deg"],   # deg will toggle degrees
    ["asin", "acos", "atan", "pi"],
    ["ln", "log", "sqrt", "fact"],  # fact -> adds '!' and will be preprocessed
    ["(", ")", "abs", "e"]
]

# Build buttons dynamically depending on mode
button_widgets = []  # for clearing later

def build_buttons():
    # clear existing
    for w in button_widgets:
        try:
            w.destroy()
        except:
            pass
    button_widgets.clear()

    # If scientific_mode, add the scientific panel at top (4x4)
    r_offset = 0
    if scientific_mode:
        # create a 4x4 grid for scientific at top of btn_frame
        for r, row in enumerate(scientific_buttons):
            for c, label in enumerate(row):
                if label == "":
                    continue
                bg = SCI_BG if label in {"deg", "pi", "e", "fact"} else NUM_BG
                fg = NUM_FG
                # map commands
                if label == "deg":
                    cmd = lambda: set_deg_mode(not deg_mode)
                    btn_font = top_button_font
                elif label == "pi":
                    cmd = lambda: add_to_display("pi")
                    btn_font = top_button_font
                elif label == "e":
                    cmd = lambda: add_to_display("e")
                    btn_font = top_button_font
                elif label == "fact":
                    cmd = lambda: add_to_display("!")  # will be converted to factorial(n)
                    btn_font = top_button_font
                else:
                    # functions add "name("
                    cmd = lambda name=label: add_to_display(f"{name}(")
                    btn_font = button_font
                btn = make_button(btn_frame, label, r, c, bg=bg, fg=fg, command=cmd, font_to_use=btn_font)
                button_widgets.append(btn)
        r_offset = len(scientific_buttons)

    # Now add the standard keypad under the scientific panel (or at top if not scientific)
    for r, row in enumerate(standard_buttons):
        for c, label in enumerate(row):
            if label == "":
                continue
            # determine grid row index
            grid_row = r + r_offset
            if label == "C":
                bg = DEL_BG; fg = DEL_FG
                cmd = clear_display
            elif label == "⌫":
                bg = NUM_BG; fg = NUM_FG
                cmd = backspace
            elif label in {"+", "-", "*", "/"}:
                bg = OP_BG; fg = OP_FG
                cmd = lambda ch=label: add_to_display(ch)
            elif label == "=":
                bg = EQUAL_BG; fg = EQUAL_FG
                cmd = evaluate_expression
            elif label == ".":
                bg = NUM_BG; fg = NUM_FG
                cmd = lambda: add_to_display(".")
            elif label == "+/-":
                bg = NUM_BG; fg = NUM_FG
                cmd = toggle_plus_minus
            elif label == "%":
                bg = OP_BG; fg = OP_FG
                cmd = lambda: add_to_display("%")
            elif label == "^":
                bg = OP_BG; fg = OP_FG
                cmd = lambda: add_to_display("^")
            elif label in {"(", ")"}:
                bg = NUM_BG; fg = NUM_FG
                cmd = lambda ch=label: add_to_display(ch)
            else:
                # digits
                bg = NUM_BG; fg = NUM_FG
                cmd = lambda ch=label: add_to_display(ch)
            btn = make_button(btn_frame, label, grid_row, c, bg=bg, fg=fg, command=cmd)
            button_widgets.append(btn)

    # configure grid weights
    total_rows = r_offset + len(standard_buttons)
    total_cols = 4
    for i in range(total_rows):
        btn_frame.rowconfigure(i, weight=1)
    for j in range(total_cols):
        btn_frame.columnconfigure(j, weight=1)

def toggle_plus_minus():
    s = display_var.get()
    if not s:
        return
    # Attempt to toggle last number
    i = len(s) - 1
    while i >= 0 and (s[i].isdigit() or s[i] == '.' or s[i] == 'e'):
        i -= 1
    last = s[i+1:]
    try:
        val = safe_eval(last)
        toggled = format_result(-val)
        display_var.set(s[:i+1] + toggled)
    except Exception:
        # fallback: simple toggle at front
        if s.startswith('-'):
            display_var.set(s[1:])
        else:
            display_var.set('-' + s)

# initial build
# place scientific toggle and clear history in top_frame
def toggle_scientific():
    global scientific_mode
    scientific_mode = not scientific_mode
    sci_btn.config(relief="sunken" if scientific_mode else "raised")
    build_buttons()

sci_btn = tk.Button(top_frame, text="Scientific", bg=SCI_BG, fg="white", font=top_button_font, bd=0, command=toggle_scientific)
sci_btn.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
clear_hist_btn = tk.Button(top_frame, text="Clear History", bg=DEL_BG, fg="white", font=top_button_font, bd=0,
                           command=lambda: (history.clear(), history_var.set(history)))
clear_hist_btn.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
deg_btn = tk.Button(top_frame, text="DEG", bg="#333333", fg="white", font=top_button_font, bd=0,
                    command=lambda: set_deg_mode(not deg_mode))
deg_btn.grid(row=0, column=2, padx=6, pady=6, sticky="nsew")

top_frame.columnconfigure(0, weight=1)
top_frame.columnconfigure(1, weight=1)
top_frame.columnconfigure(2, weight=1)

build_buttons()

# Keyboard bindings
def on_key(event):
    key = event.keysym
    ch = event.char
    if ch.isdigit():
        add_to_display(ch)
    elif ch in "+-*/().%":
        add_to_display(ch)
    elif ch == '^':
        add_to_display("^")
    elif ch == '!':
        add_to_display("!")
    elif key == "Return":
        evaluate_expression()
    elif key == "BackSpace":
        backspace()
    elif key == "Escape":
        clear_display()
    elif ch == '.':
        add_to_display(".")
    # allow entering function names via keyboard (e.g., 's' for sin) - not auto-complete

root.bind_all("<Key>", on_key)

root.mainloop()
