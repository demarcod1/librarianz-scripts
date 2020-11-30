from gui.util.multiselect import Multiselect
from tkinter import *
from tkinter import ttk

class DollieOptions(ttk.Frame):

    def __init__(self, parent, options, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Dollie chartz
        self.dollie_songs_selection = Multiselect(self, input=options['dollie-songs'],
                                    title='Select Dollie Songs',
                                    header='Chart Name',
                                    addText='Add Chart',
                                    warn=False,
                                    orient='vertical',
                                    height=15)
        self.dollie_songs_selection.grid(row=0, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        # Make resizeable
        self.rowconfigure(0, weight='1')
        self.columnconfigure(0, weight='1')
    
    def get_dollie_options(self):
        return { 'dollie-songs': self.dollie_songs_selection.get_chosen_values() }