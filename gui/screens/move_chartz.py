from gui.util.util import bind_button
from gui.util.multiselect import Multiselect
from gui.util.script_progress import ScriptProgress
from scripts.move_chartz import move_chartz
from scripts.util.util import parse_options, write_options
from tkinter import *
from tkinter import ttk

class MoveChartzScreen(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Parse move_chartz options
        self.options = parse_options("move_chartz_options.json")

        # Move chartz selection
        self.new_chartz = Multiselect(self, input=self.options['chartz'],
                                        title='Chartz to Move',
                                        key1='name', 
                                        key2='to',
                                        header='Chart Name',
                                        addText='Add Chart',
                                        orient='vertical',
                                        height=10,
                                        archive=True)
        self.new_chartz.grid(row=0, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Run script/Close buttons
        close_button = ttk.Button(self, text='Close', command=lambda: parent.master.destroy())
        bind_button(close_button)
        run_script_button = ttk.Button(self, text='Move Chartz', command=self.run_script)
        bind_button(run_script_button)

        close_button.grid(row=1, column=0, sticky=(S, W), padx=20, pady=10)
        run_script_button.grid(row=1, column=1, sticky=(S, E), padx=20, pady=10)

        # Allow resizing
        self.rowconfigure(1, weight="1")
        self.columnconfigure(1, weight="1")

    
    def run_script(self, *args):
        # Update and write to options
        self.options["chartz"] = self.new_chartz.get_chosen_values('name', 'to')
        write_options(self.options, "move_chartz_options.json")

        # Re-show main window
        def callback(code):
            self.master.master.deiconify()
            print(f"Thread Finished with code {code}")
        

        ScriptProgress(self, script=move_chartz, callback=callback, title="Moving Chartz", name="Move Chartz")
        self.master.master.withdraw()