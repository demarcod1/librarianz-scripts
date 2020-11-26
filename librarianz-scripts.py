import sys
import tkinter as tk
from getopt import getopt, GetoptError

from scripts.download_parts import download_parts
from scripts.folder_creator import folder_creator
from scripts.login import login
from scripts.move_chartz import move_chartz
from scripts.redvest_creator import redvest_creator
from scripts.separated_folders_creator import separated_folders_creator
from scripts.upload_files import upload_files
from scripts.validate_folder_files import validate_folder_files

SCRIPT_DICT = {
    "download_parts": download_parts,
    "login" : login,
    "folder_creator": folder_creator,
    "move_chartz": move_chartz,
    "redvest_creator": redvest_creator,
    "separated_folders_creator": separated_folders_creator,
    "upload_files": upload_files,
    "validate_folder_files": validate_folder_files
}

def print_help():
    print("\nUsage: librarianz-scripts.py [-s <script-name>]\n")
    print("script-name can be one of the following:\n", list(SCRIPT_DICT.keys()))
    print("\nFor more details, check readme at https://github.com/demarcod1/librarianz-scripts/blob/main/README.md\n\n")

def main(argv):
    script = None

    # Parse command line inputs
    try:
        opts, args = getopt(argv, "hs:", [ "script=", "help" ])
    except GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg, in opts:
        if opt in ["-h", "--help"]:
            print_help()
            sys.exit()
        elif opt in ["-s", "--script"]:
            if arg in SCRIPT_DICT:
                script = SCRIPT_DICT[arg]
            else:
                print_help()
                sys.exit()
    
    # If a script is specified on the command line - run it!
    if script:
        script()
        return
    
    window = tk.Tk()
    greeting = tk.Label(text="Hello, Tkinter")
    greeting.pack()
    window.mainloop()

if __name__ == '__main__':
    main(sys.argv[1:])