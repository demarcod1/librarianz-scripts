import os
from scripts.util.util import make_application_data, parse_options, resourcePath, write_options
from gui.screens.folder_creator import FolderCreatorScreen
from gui.screens.redvest_creator import RedvestCreatorScreen
from gui.screens.move_chartz import MoveChartzScreen
from gui.screens.upload_files import UploadFilesScreen
from tkinter import *
from tkinter import ttk, filedialog
from appdirs import user_data_dir

class MainMenu:

    def __init__(self, parent, data_dir):

        # Set title
        parent.title("Digital Library Manager")
        parent.iconphoto(True, PhotoImage(file=resourcePath(os.path.join('res', 'icons', 'embo.png'))))
        parent.minsize(600, 550)

        # Prompt user to specify credentials path
        res_options = parse_options("res_paths.json", from_=data_dir)
        creds_path = res_options['creds-path']
        if not os.path.exists(creds_path) or not os.path.isfile(creds_path):
            new_path = filedialog.askopenfilename(title='Select Credentials File', filetypes=[('Credentials JSON File','*.json')])
            if new_path != None:
                res_options['creds-path'] = new_path
                write_options(res_options, "res_paths.json")

        # Create notebook
        n = ttk.Notebook(parent, width=650, height=600, padding=5)

        # Add each frame to the notebook
        folder_creator_frame = FolderCreatorScreen(n)
        upload_files_frame = UploadFilesScreen(n)
        move_chartz_frame = MoveChartzScreen(n)
        redvest_creator_frame = RedvestCreatorScreen(n)

        n.add(folder_creator_frame, text='Folder Creator', underline=0)
        n.add(move_chartz_frame, text='Move Chartz', underline=0)
        n.add(redvest_creator_frame, text='Redvest Creator', underline=0)
        n.add(upload_files_frame, text='Upload Files', underline=0)
        
        n.enable_traversal()
        n.grid(row=0, column=0, sticky=(N, E, S, W))

        # Allow resizing
        parent.columnconfigure(0, weight='1', minsize=350)
        parent.rowconfigure(0, weight='1', minsize=250)