import threading
from tkinter import *
from tkinter import ttk

# Automatically bind the key
def bind_button(button: ttk.Button):
    button.bind("<Key-Return>", lambda e: button.invoke())
    button.bind("<KP_Enter>", lambda e: button.invoke())

# Spawn a thread to run the script
def spawn_thread(script, callback):

    # Define target that the thread should run
    def target():
        try:
            res = script()
            if res == None: res = 1
            callback(res)
        except:
            callback(1)
    
    thread = threading.Thread(target=target, daemon=True)
    thread.start()