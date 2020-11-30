from gui.util.util import validate_numerical_entry
from gui.screens.options.util.font_select import FontSelect
from tkinter import *
from tkinter import ttk

class TOCOptions(ttk.Frame):

    def __init__(self, parent, options, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Add Heading font select
        self.heading_select = FontSelect(self, 0,
                                            title='Table of Contents Header',
                                            name='Heading',
                                            leftEntry=options['toc']['title']['label'],
                                            middleEntry=options['toc']['title']['font'],
                                            rightEntry=options['toc']['title']['size'])
        self.heading_select.grid(row=0, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Add Entry font select
        self.entry_select = FontSelect(self, 1,
                                        title='Table Entry Format',
                                        leftLabel='Dollie Songs Font',
                                        leftEntry=options['toc']['entry']['font-dollie'],
                                        middleLabel='Normal Songs Font',
                                        middleEntry=options['toc']['entry']['font-normal'],
                                        rightEntry=options['toc']['entry']['size'])
        self.entry_select.grid(row=1, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        # Add num columns selector
        # Add width/height selectors
        num_cols_frame = ttk.Labelframe(self, text='Column Count')
        validate_fn = (num_cols_frame.register(validate_numerical_entry(False)), '%P')

        self.num_cols = StringVar()
        self.num_cols.set(options['toc']['num-cols'])
        num_cols_spinbox = ttk.Spinbox(num_cols_frame, from_=0, to=5, increment=1, width=3, textvariable=self.num_cols, validate='key', validatecommand=validate_fn)
        num_cols_spinbox.grid(row=0, column=0, padx=10, pady=5)
        num_cols_spinbox.bind('<FocusOut>', lambda _: self.num_cols.set(options['toc']['num-cols']) if not len(self.num_cols.get()) else '')

        num_cols_frame.bind('<Button-1>', lambda e: e.widget.focus_set())
        num_cols_frame.rowconfigure(0, weight='1')
        num_cols_frame.columnconfigure(0, weight='1')
        num_cols_frame.grid(row=1, column=1, sticky=(N, E, S, W), padx=20, pady=10)

        # Add Heading font select
        self.footer_select = FontSelect(self, 0,
                                            title='Table of Contents Footer',
                                            name='Footer',
                                            leftEntry=options['toc']['footer']['label'],
                                            middleEntry=options['toc']['footer']['font'],
                                            rightEntry=options['toc']['footer']['size'])
        self.footer_select.grid(row=2, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Allow resizing
        for row in range(3):
            self.rowconfigure(row, weight="1")
        self.columnconfigure(0, weight="1")
    
    def get_toc_options(self):
        res = {}

        heading_res = self.heading_select.get_font_select()
        res['title'] = { 'label': heading_res[0], 'font': heading_res[1], 'size': heading_res[2] }

        entry_res = self.entry_select.get_font_select()
        res['entry'] = { 'font-dollie': entry_res[0], 'font-normal': entry_res[1], 'size': entry_res[2] }

        footer_res = self.footer_select.get_font_select()
        res['footer'] = { 'label': footer_res[0], 'font': footer_res[1], 'size': footer_res[2] }

        res['num-cols'] = int(self.num_cols.get())
    
        return res