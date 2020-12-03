from scripts.util.util import CredentialsError
import threading
from tkinter import *
from tkinter import ttk
       
# Automatically bind the key
def bind_button(button: ttk.Button):
    button.bind("<Key-Return>", lambda e: button.invoke())
    button.bind("<KP_Enter>", lambda e: button.invoke())

# Spawn a thread to run the script
def spawn_thread(script, callback, scriptName='Script'):

    # Define target that the thread should run
    def target():
        try:
            print(f"Starting {scriptName} script...")
            res = script()
            if res == None: res = 1
            callback(res)
        except SystemExit:
            callback(2)
        except CredentialsError as e:
            print(e)
            callback(3)
        except Exception as e:
            print(f'ERROR: {scriptName} crashed during execution')
            print("Error Trace:", e)
            callback(1)
    
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread

# Validate that a spinbox entry is a number
def validate_numerical_entry(is_float=False):
    def validator(newval):
        if len(newval) == 0: return True
        try:
            float(newval) if is_float else int(newval)
            return True
        except ValueError:
            return False
    return validator