import threading

stop_script = threading.Event()

print_lock = threading.Lock()

def reset_stop_script():
    stop_script.clear()

def stop_scripts():
    stop_script.set()

def check_stop_script(crash=True):
    if stop_script.is_set() and crash:
        raise SystemExit
    else:
        return stop_script.is_set()

def thread_print(*args):
    with print_lock:
        print(*args)