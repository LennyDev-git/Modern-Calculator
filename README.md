# 🧮 Scientific Calculator (Tkinter)

A modern **scientific calculator** built with Python and Tkinter.  
It features a dark-themed interface, a secure AST-based math evaluator, scientific functions, degree/radian mode, implicit multiplication, and calculation history.

---

## 🚀 Features

### 🧮 Standard Functions
- Basic arithmetic: `+`, `-`, `*`, `/`
- Power operator `^`
- Percentage support (`50%` → `0.5`)
- Parentheses `()`
- Decimal numbers
- Sign toggle (`+/-`)
- Backspace (`⌫`)
- Clear display (`C`)
- Full keyboard support

---

### 🔬 Scientific Mode
Toggle **Scientific** mode to access advanced functions:

- Trigonometric: `sin`, `cos`, `tan`
- Inverse trig: `asin`, `acos`, `atan`
- Logarithms: `ln`, `log`, `log10`
- Square root: `sqrt`
- Factorial: `n!`
- Absolute value: `abs`
- Constants: `pi`, `e`
- Degree/Radian toggle (`DEG`)

---

## 📐 Degree / Radian Mode

- Default: **Radians**
- Toggle `DEG` to switch to **Degrees**
- Affects all trigonometric and inverse trigonometric functions

---

## 🧠 Smart Expression Handling

The calculator automatically preprocesses input:

- `^` → converted to `**`
- `50%` → `(50/100)`
- `5!` → `factorial(5)`
- Implicit multiplication:
  - `2pi` → `2*pi`
  - `2(3+4)` → `2*(3+4)`
  - `(2+3)4` → `(2+3)*4`
- Unicode normalization:
  - `π` → `pi`
  - `×` → `*`
  - `−` → `-`

---

## 🔒 Safe Evaluation

Expressions are parsed using Python’s `ast` module with a strict whitelist:

- Only approved operators allowed
- Only approved functions/constants allowed
- Division-by-zero protection
- Invalid characters rejected
- No arbitrary code execution possible

---

## 📜 History

- Stores up to 12 previous calculations
- Displays expression and result
- Clearable with **"Clear History"**

---

## 🖥️ Requirements

- Python 3.8+
- Tkinter (included with most Python installations)

---

## ▶️ How to Run

```bash
python calculator.py
```

Or run the Windows executable (if provided):

```bash
calculator.exe
```

---

## ⌨️ Keyboard Shortcuts

| Key        | Action                  |
|------------|--------------------------|
| `0-9`      | Numbers                  |
| `+ - * /`  | Operators                |
| `^`        | Power                    |
| `!`        | Factorial                |
| `.`        | Decimal point            |
| `Enter`    | Evaluate expression      |
| `Backspace`| Delete last character    |
| `Escape`   | Clear display            |

---

## 📂 Project Structure

```
calculator.py
README.md
```

---

## 🎨 UI Design

- Modern dark theme
- Hover button effects
- Color-coded buttons:
  - Operators (Blue)
  - Equal (Green)
  - Clear (Red)
  - Scientific (Purple)

---

## 📄 License

Feel free to use, modify, and share this project.
