from gui.util.util import validate_numerical_entry
from scripts.util.util import parse_options
from tkinter import *
from tkinter import ttk

class FontSelect(ttk.Labelframe):

    # Mode 0 -> add label entry option
    # Mode 1 -> add second font select option
    def __init__(self, parent, mode, *args, **kwargs):
        # Initialize superclass
        title = kwargs.get('title') or 'Select Font'
        ttk.LabelFrame.__init__(self, parent, text=title)

        # Initializes props
        name = kwargs.get('name') or 'Entry'

        # Supported fonts
        fonts_dict = parse_options("supported_fonts.json")
        supported_fonts: List = fonts_dict['default']
        if fonts_dict.get('more'):
            more: List = fonts_dict['more']
            more.sort()
            supported_fonts.extend(more)


        # Leftmost entry is either a text entry or a font select, depending on mode
        left_label_text = kwargs.get('leftLabel') or f'{name} Text:'
        self.left_entry_text = StringVar()
        if mode == 0:
            left_label = ttk.Label(self, text=left_label_text)
            left_label.grid(row=0, column=0, sticky=S, padx=10, pady=2)

            self.left_entry_text.set(kwargs.get('leftEntry') or '')
            left_entry = ttk.Entry(self, textvariable=self.left_entry_text)
            left_entry.grid(row=1, column=0, sticky=N, padx=10, pady=2)
        elif mode == 1:
            left_label = ttk.Label(self, text=left_label_text)
            left_label.grid(row=0, column=0, sticky=S, padx=10, pady=2)

            self.left_entry_text.set(kwargs.get('leftEntry') or 'Courier')
            left_combobox = ttk.Combobox(self, textvariable=self.left_entry_text)
            left_combobox['values'] = supported_fonts
            left_combobox.state(['readonly'])
            left_combobox.grid(row=1, column=0, sticky=N, padx=10, pady=2)
        

        # Middle entry is alwas a font select
        middle_label = ttk.Label(self, text=kwargs.get('middleLabel') or f'{name} Font:')
        middle_label.grid(row=0, column=1 - (mode > 1), sticky=S, padx=10, pady=2)

        self.middle_entry_text = StringVar()
        self.middle_entry_text.set(kwargs.get('middleEntry') or 'Courier')
        middle_combobox = ttk.Combobox(self, textvariable=self.middle_entry_text)
        middle_combobox['values'] = supported_fonts
        middle_combobox.state(['readonly'])
        middle_combobox.grid(row=1, column=1 - (mode > 1), sticky=N, padx=10, pady=2)

        # Right entry is always a size selection
        validate_fn = (self.register(validate_numerical_entry(False)), '%P')

        right_label = ttk.Label(self, text=kwargs.get('rightLabel') or 'Font Size:')
        right_label.grid(row=0, column=2 - (mode > 1), sticky=S, padx=10, pady=2)

        self.right_entry_val = StringVar()
        self.right_entry_val.set(kwargs.get('rightEntry') or 12)
        right_spinbox = ttk.Spinbox(self, from_=6, to=36, increment=2, textvariable=self.right_entry_val, width=3, validate='key', validatecommand=validate_fn)
        right_spinbox.bind('<FocusOut>', lambda _: self.right_entry_val.set(kwargs.get('rightLabel') or 12) if not len(self.right_entry_val.get()) else '')
        right_spinbox.grid(row=1, column=2 - (mode > 1), sticky=N, padx=10, pady=2)
        self.bind('<Button-1>', lambda e: e.widget.focus_set())

        # Make resizeable
        for col in range(3 - (mode > 1)):
            self.columnconfigure(col, weight='1')
        self.rowconfigure(0, weight='1')
        self.rowconfigure(1, weight='1')
    
    def get_font_select(self):
        right_entry = self.right_entry_val.get()
        return (self.left_entry_text.get(), self.middle_entry_text.get(), int(right_entry))