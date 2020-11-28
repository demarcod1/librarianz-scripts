from gui.screens.move_chartz import MoveChartzScreen
from gui.screens.upload_files import UploadFilesScreen
from tkinter import *
from tkinter import ttk

class NotebookTest:

    def __init__(self, parent):

        # Set title
        parent.title("Digital Library Manager")
        parent.minsize(600, 550)

        # Create notebook
        n = ttk.Notebook(parent, width=650, height=600)

        # Add each frame to the notebook
        folder_creator_frame = ttk.Frame(n, relief='solid')
        upload_files_frame = UploadFilesScreen(n)
        move_chartz_frame = MoveChartzScreen(n)
        redvest_creator_frame = ttk.Frame(n, relief='groove')

        n.add(folder_creator_frame, text='Folder Creator')
        n.add(upload_files_frame, text='Upload Files')
        n.add(move_chartz_frame, text='Move Chartz')
        n.add(redvest_creator_frame, text='Redvest Creator')
        
        n.enable_traversal()
        n.grid(row=0, column=0, sticky=(N, E, S, W))

        # Allow resizing
        n.rowconfigure(0, weight='1')
        n.columnconfigure(0, weight='1')
        
        parent.columnconfigure(0, weight='1', minsize=350)
        parent.rowconfigure(0, weight='1', minsize=250)