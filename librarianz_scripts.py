from scripts.util.util import is_frozen, make_application_data, parse_options, write_options
from appdirs import user_data_dir
from gui.main_menu import MainMenu
import sys
import tkinter as tk
from getopt import getopt, GetoptError

from scripts.download_parts import download_parts
from scripts.folder_creator import folder_creator
from scripts.login import login
from scripts.move_chartz import move_chartz
from scripts.redvest_creator import redvest_creator
from scripts.remake_shortcuts import remake_shortcuts
from scripts.separated_folders_creator import separated_folders_creator
from scripts.upload_files import upload_files
from scripts.validate_folder_files import validate_folder_files

VERSION = '0.1.3'

SCRIPT_DICT = {
    "download_parts": download_parts,
    "login" : login,
    "folder_creator": folder_creator,
    "move_chartz": move_chartz,
    "redvest_creator": redvest_creator,
    "remake_shortcuts": remake_shortcuts,
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
    
         
    # Search for application data directory
    data_dir=None
    if is_frozen():
        data_dir = user_data_dir('LSJUMB Librarianz Scripts', 'LSJUMB', VERSION)
        res_options = parse_options("res_paths.json", from_=data_dir)
        res_options['res-path'] = data_dir
        make_application_data(data_dir, VERSION != res_options.get('version'))
        res_options['version'] = VERSION
        write_options(res_options, "res_paths.json")
        write_options(res_options, "res_paths.json")

    # Run Main Application
    root = tk.Tk()
    MainMenu(root, data_dir)
    root.mainloop()

if __name__ == '__main__':
    main(sys.argv[1:])