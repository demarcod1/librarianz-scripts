from gui.screens.options.options_parent import OptionsParent
from gui.util.util import bind_button
from scripts.folder_creator import folder_creator
from scripts.validate_folder_files import validate_folder_files
from scripts.download_parts import download_parts
from gui.util.script_progress import ScriptProgress
from gui.util.folder_creator_workflow import FolderCreatorWorkflow
from gui.util.labeled_entry import LabledEntry
from gui.util.select_directory import SelectDirectory
from scripts.util.util import parse_options, write_options
from tkinter import *
from tkinter import ttk
import platform

class FolderCreatorScreen(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Parse folder creator options
        self.options = parse_options("folder_creator_options.json")

        # Target Directory selection
        self.select_directory = SelectDirectory(self, path=self.options["folder-dir"], title='Select Target Directory')
        self.select_directory.grid(row=0, column=0, columnspan=3, sticky=(N, E, S, W), padx=20, pady=10)

        # Folder Name Selection
        self.folder_name_entry = LabledEntry(self, title='Enter Folder Name', label='LSJUMB Folder Name', defaultEntry=self.options['folder-name'])
        self.folder_name_entry.grid(row=1, column=0, sticky=(N, S, W, E), padx=20, pady=10)

        # Verbose Output Selection
        verbose_frame = ttk.LabelFrame(self, text='Console Output')

        self.verbose = BooleanVar()
        self.verbose.set(self.options['verbose'])
        verbose_checkbox = ttk.Checkbutton(verbose_frame, text='Verbose Logging', variable=self.verbose)
        verbose_checkbox.grid(row=0, column=0, padx=10, pady=5)
        verbose_frame.rowconfigure(0, weight='1')
        verbose_frame.columnconfigure(0, weight='1')

        verbose_frame.grid(row=1, column=1, sticky=(N, E, S, W), padx=20, pady=10)

        # Workflows
        workflow_frame = ttk.Frame(self)

        # Download Files Workflow
        dl_workflow = FolderCreatorWorkflow(parent=workflow_frame,
                                            description="Downloads files from the Digial Library onto your local machine at the target directory specified above",
                                            scriptButtonName="Download Files",
                                            scriptCallback=self.runDownloadScript,
                                            optionsCallback=lambda: self.open_options(0))
        dl_workflow.grid(row=0, column=0, sticky=(N, E, S, W), padx=0, pady=5)

        # Validate Folders Workflow
        validate_workflow = FolderCreatorWorkflow(parent=workflow_frame,
                                                description="Validates the folder structure at the target directory, and optionally outputs a sample table of contents",
                                                scriptButtonName='Validate Folder',
                                                scriptCallback=self.runValidateScript,
                                                optionsCallback=lambda: self.open_options(1))
        validate_workflow.grid(row=0, column=1, sticky=(N, E, S, W), padx=20, pady=5)

        # Create Folders workflow
        create_folders = FolderCreatorWorkflow(parent=workflow_frame,
                                                description="Writes the folders to the Output folder in the target directory\n\nThis takes about 3-5 mins to complete per part",
                                                scriptButtonName='Generate Folders',
                                                scriptCallback=self.runFolderCreatorScript,
                                                optionsCallback=lambda: self.open_options(2))
        create_folders.grid(row=0, column=2, sticky=(N, E, S, W), padx=0, pady=5)

        # Make Workflow Frame resizeable
        workflow_frame.grid(row=2, column=0, columnspan=3, sticky=(N, E, S, W), padx=20, pady=10)
        workflow_frame.rowconfigure(0, weight='1')
        for i in range(3): workflow_frame.columnconfigure(i, weight='1')
        
        # Run script/Close buttons
        close_button = ttk.Button(self, text='Close', command=lambda: parent.master.destroy())
        bind_button(close_button)

        close_button.grid(row=3, column=0, sticky=(S, W), padx=20, pady=10)

        # Make resizeable
        for i in range(4):
            self.rowconfigure(i, weight='1')
        self.columnconfigure(1, weight='1')
    
    def write_options_and_withdraw(self):
        self.options['verbose'] = self.verbose.get()
        self.options['folder-dir'] = self.select_directory.get_path()
        self.options['folder-name'] = self.folder_name_entry.get_entry()
        write_options(self.options, "folder_creator_options.json")

        self.master.master.withdraw()

    # Re-show main window
    def script_callback(self, code):
        self.master.master.deiconify()
        print(f"Thread Finished with code {code}")

    def options_callback(self):
        self.master.master.deiconify()

    def open_options(self, tab):
        self.withdraw_self()
        OptionsParent(self, self.options, self.options_callback, tab=tab)
    
    def withdraw_self(self):
        self.master.master.withdraw()

    def runDownloadScript(self):
        self.write_options_and_withdraw()
        ScriptProgress(self, script=download_parts, callback=self.script_callback, title='Downloading Parts from Digital Library...', name='Parts Downloader', safe=True)
        

    def runValidateScript(self):
        self.write_options_and_withdraw()
        ScriptProgress(self, script=validate_folder_files, callback=self.script_callback, title='Validating Target Directory...', name='Folder + File Validation', safe=True)
    
    def runFolderCreatorScript(self):
        def folder_creator_wrapper():
            print("WARNING: Running this script with the UI active takes significantly more time due to python threading limitations")
            print(f'To generate the folder faster, run "{"py" if platform.system() == "Windows" else "python3"} librarianz_scripts.py -s folder_creator"')
            folder_creator()
        
        self.withdraw_self()
        ScriptProgress(self, script=folder_creator_wrapper, callback=self.script_callback, title='Generating Folders...', name='Folder Creator', safe=True)