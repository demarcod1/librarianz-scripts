from gui.util.util import bind_button, spawn_thread
from tkinter import *
from tkinter import ttk, messagebox

class ScriptProgress(Toplevel):

    def __init__(self, parent, script, callback, *args, **kwargs):
        # Set variables
        self.script = script
        self.callback = callback
        self.destroy_after_callback = False
        self.active = True
        self.name = kwargs.get("name") or "Script"
        title = kwargs.get("title") or "Script Progress"
        geometry = kwargs.get("geometry")
        self.old_stdout = sys.stdout

        # Initialize window
        Toplevel.__init__(self, parent)
        self.attributes("-topmost", 1)
        self.title(title)
        self.resizable(FALSE, FALSE)
        self.geometry(geometry or "475x300")
        self.protocol("WM_DELETE_WINDOW", self.destroy_self)

        # Create label
        self.label = ttk.Label(self, text=f'{self.name} script in progress...')
        self.label.grid(row=0, column=0, sticky=(N, S, E, W), padx=20, pady=2)

        # Create progressbar 
        self.prog_bar = ttk.Progressbar(self, orient='horizontal', mode='indeterminate', length=200)
        self.prog_bar.start(25)
        self.prog_bar.grid(row=1, column=0, sticky=(N, E, W), padx=20, pady=2)

        # Create text console area within dummy frame
        dummy_frame = ttk.Frame(self)

        self.console = Text(dummy_frame, width=50, height=8, wrap='none')
        self.console["state"] = "disabled"
        self.console.grid(row=0, column=0, sticky=(N, E, S, W))
        self.console.tag_configure('warning', foreground='Orange')
        self.console.tag_configure('error', foreground='Red')
        self.console.tag_configure('success', foreground='Green')
        self.console.tag_config('normal', foreground='Black')

        scrollx = ttk.Scrollbar(dummy_frame, orient='horizontal', command=self.console.xview)
        scrolly = ttk.Scrollbar(dummy_frame, orient='vertical', command=self.console.yview)
        self.console['xscrollcommand'] = scrollx.set
        self.console['yscrollcommand'] = scrolly.set
        scrollx.grid(row=1, column=0, sticky=(E, W, N, S))
        scrolly.grid(row=0, column=1, sticky=(N, S, E, W))
        
        dummy_frame.grid(row=2, column=0, padx=20, pady=2, sticky=(N, S, E, W))

        # Map stdout to this console
        class RedirectStdout(object):
            def __init__(self, text_area: Text):
                self.text_area = text_area
            
            def write(self, str):
                self.text_area['state'] = 'normal'
                self.text_area.insert("end", str, self.add_tags(str))
                self.text_area.see("end")
                self.text_area['state'] = 'disabled'
            
            def add_tags(self, str):
                if 'WARNING' in str:
                    return ('warning')
                elif 'ERROR' in str:
                    return ('error')
                elif 'uccess' in str:
                    return ('success')
                else:
                    return ('none')

        sys.stdout = RedirectStdout(self.console)

        # Create abort/return button
        self.button_text = StringVar()
        self.button_text.set(f'Abort {self.name} script')
        main_button = ttk.Button(self, textvariable=self.button_text, command=self.destroy_self)
        bind_button(main_button)
        main_button.grid(row=3, column=0, sticky=S, padx=20, pady=10)

        # Allow resizing
        self.columnconfigure(0, weight="1")
        self.columnconfigure(1, weight="1")
        for row in range(4):
            self.rowconfigure(row, weight="1")
        
        # Start thread
        def inner_callback(code):
            self.deactivate()
            self.callback(code)
            if (self.destroy_after_callback): self.destroy()

        self.thread = spawn_thread(self.script, inner_callback, self.name)
    
    # Logic for deactivation
    def deactivate(self):
        sys.stdout = self.old_stdout
        self.prog_bar.stop()
        self.active = False
        self.button_text.set("Return to Main Menu")
        self.label['text'] = f'Finished running {self.name} script'
    
    # Logic for self-destruction
    def destroy_self(self):
        if self.active and hasattr(self, 'thread'):
            if messagebox.askokcancel(title='Running Script', message=f'Are you sure you wish to abort the {self.name} script?'):
                self.thread.kill()
                self.destroy_after_callback = True
        else: self.destroy()