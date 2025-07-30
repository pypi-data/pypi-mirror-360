import tkinter as tk
from tkinter import font

# Logic functions
def dec2bin(decimal):
    if decimal < 0:
        raise ValueError("Decimal number must be non-negative")
    return bin(decimal)[2:]

def bin2dec(binary_str):
    if not all(char in "01" for char in binary_str):
        raise ValueError("Binary input must only contain 0 or 1")
    return str(int(binary_str, 2))

def asciitobin(text):
    if not text:
        raise ValueError("Input cannot be empty")
    return ' '.join(format(ord(char), '08b') for char in text)

# GUI logic
def convert_dec2bin(*args):
    try:
        decimal = int(entry_dec.get())
        result_bin.set(dec2bin(decimal))
    except Exception as e:
        result_bin.set(f"Error: {e}")

def convert_bin2dec(*args):
    try:
        binary = entry_bin.get()
        result_dec.set(bin2dec(binary))
    except Exception as e:
        result_dec.set(f"Error: {e}")

def convert_ascii2bin(*args):
    try:
        text = entry_ascii.get()
        result_ascii.set(asciitobin(text))
    except Exception as e:
        result_ascii.set(f"Error: {e}")

# GUI setup
root = tk.Tk()
root.title("decitobin 1.2 – 3-in-1 Converter")
root.geometry("600x400")
root.resizable(False, False)
f = font.Font(family="Arial", size=12)

# Decimal to Binary
tk.Label(root, text="Decimal ➜ Binary", font=f).pack(pady=(10, 5))
entry_dec = tk.Entry(root, font=f, justify="center")
entry_dec.pack()
tk.Button(root, text="Convert", font=f, command=convert_dec2bin).pack(pady=2)
result_bin = tk.StringVar()
tk.Entry(root, font=f, textvariable=result_bin, justify="center", state="readonly", fg="#007acc").pack(pady=(0, 10))

# Binary to Decimal
tk.Label(root, text="Binary ➜ Decimal", font=f).pack(pady=(5, 5))
entry_bin = tk.Entry(root, font=f, justify="center")
entry_bin.pack()
tk.Button(root, text="Convert", font=f, command=convert_bin2dec).pack(pady=2)
result_dec = tk.StringVar()
tk.Entry(root, font=f, textvariable=result_dec, justify="center", state="readonly", fg="#dd6600").pack(pady=(0, 10))

# ASCII to Binary
tk.Label(root, text="ASCII Text ➜ Binary", font=f).pack(pady=(5, 5))
entry_ascii = tk.Entry(root, font=f, justify="center")
entry_ascii.pack()
tk.Button(root, text="Convert", font=f, command=convert_ascii2bin).pack(pady=2)
result_ascii = tk.StringVar()
tk.Entry(root, font=f, textvariable=result_ascii, justify="center", state="readonly", fg="#22aa88").pack(pady=(0, 10))

# Bind Enter key
root.bind('<Return>', convert_dec2bin)

root.mainloop()