from gui.screens.options.util.toc_font_select import TOCFontSelect
from tkinter import *
from tkinter import ttk

class TOCOptions(ttk.Frame):

    def __init__(self, parent, options, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Retrieve options
        self.options = options

        # Add Heading font select
        self.heading_select = TOCFontSelect(self, 0,
                                            title='Table of Contents Header',
                                            name='Heading',
                                            leftEntry=self.options['toc']['title']['label'],
                                            middleEntry=self.options['toc']['title']['font'],
                                            rightEntry=self.options['toc']['title']['size'])
        self.heading_select.grid(row=0, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        # Add Entry font select
        self.entry_select = TOCFontSelect(self, 1,
                                        title='Table Entry Format',
                                        leftLabel='Dollie Songs Font',
                                        leftEntry=self.options['toc']['entry']['font-dollie'],
                                        middleLabel='Normal Songs Font',
                                        middleEntry=self.options['toc']['entry']['font-normal'],
                                        rightEntry=self.options['toc']['entry']['size'])
        self.entry_select.grid(row=1, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        # Add Heading font select
        self.footer_select = TOCFontSelect(self, 0,
                                            title='Table of Contents Footer',
                                            name='Footer',
                                            leftEntry=self.options['toc']['footer']['label'],
                                            middleEntry=self.options['toc']['footer']['font'],
                                            rightEntry=self.options['toc']['footer']['size'])
        self.footer_select.grid(row=2, column=0, sticky=(N, E, S, W), padx=20, pady=10)

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
    
        return res