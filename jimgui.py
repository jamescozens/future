import tkinter as tk

def hello(event):
    print("Single Click, Button-l")
def quit(event):
    print("Double Click, so let's stop")
    import sys; sys.exit()

# Create a main window
window = tk.Tk()
window.title("Tkinter Example")

# Create a label widget
label = tk.Label(window, text="Hello, Tkinter!")
label.pack()

# Create a button widget
button = tk.Button(window, text="Click me")
button.pack()

button.bind('<Button-1>', hello)
button.bind('<Double-1>', quit)

# Start the Tkinter event loop
window.mainloop()