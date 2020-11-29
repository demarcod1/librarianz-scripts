from gui.screens.folder_creator import FolderCreatorScreen
from gui.screens.redvest_creator import RedvestCreatorScreen
from gui.screens.move_chartz import MoveChartzScreen
from gui.screens.upload_files import UploadFilesScreen
from tkinter import *
from tkinter import ttk

class MainMenu:

    def __init__(self, parent):

        # Set title
        parent.title("Digital Library Manager")
        parent.minsize(600, 550)

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