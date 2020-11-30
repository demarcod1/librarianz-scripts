from gui.util.multiselect import Multiselect
from tkinter import *
from tkinter import ttk

class ChartzOptions(ttk.Frame):

    def __init__(self, parent, options, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Lettered Chartz
        self.lettered_selection = Multiselect(self, input=options['lettered-chartz'],
                                    title='Select Lettered Chartz',
                                    header='Chart Name',
                                    addText='Add Chart',
                                    warn=False,
                                    orient='vertical',
                                    height=10)
        self.lettered_selection.grid(row=0, column=0, rowspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Teazers
        self.teaszers_selection = Multiselect(self, input=options['teazers']['titles'],
                                    title='Select Teazers',
                                    header='Chart Name',
                                    addText='Add Chart',
                                    warn=False,
                                    orient='vertical',
                                    height=3)
        self.teaszers_selection.grid(row=0, column=1, sticky=(N, E, S, W), padx=20, pady=10)

        # Fingering chart
        self.fingering_chart_selection = Multiselect(self, input=options['fingering-chart']['titles'],
                                    title='Select Fingering Chart Files',
                                    header='File Name',
                                    addText='Add File',
                                    warn=False,
                                    orient='vertical',
                                    height=1)
        self.fingering_chart_selection.grid(row=1, column=1, sticky=(N, E, S, W), padx=20, pady=10)

        # Select whether to include teazers + fingering chart in output
        include_frame = ttk.LabelFrame(self, text='Include Teazers and Fingering Chart in Folders')

        self.incl_teazers = BooleanVar()
        self.incl_teazers.set(options['teazers']["include"])
        incl_teazers_check = ttk.Checkbutton(include_frame, text='Include Teazers', variable=self.incl_teazers)
        incl_teazers_check.grid(row=0, column=0, sticky=E, padx=10, pady=5)

        self.incl_fingering = BooleanVar()
        self.incl_fingering.set(options['fingering-chart']['include'])
        incl_fingering_check = ttk.Checkbutton(include_frame, text='Include Fingering Chart', variable=self.incl_fingering)
        incl_fingering_check.grid(row=0, column=1, sticky=W, padx=10, pady=5)

        include_frame.rowconfigure(0, weight='1')
        include_frame.columnconfigure(0, weight='1')
        include_frame.columnconfigure(1, weight='1')

        include_frame.grid(row=2, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        # Allow resizing
        for row in range(3):
            self.rowconfigure(row, weight="1")
        self.columnconfigure(1, weight="1")
        self.columnconfigure(0, weight="1")
    
    def get_chart_options(self):
        return {
            'lettered-chartz': self.lettered_selection.get_chosen_values(),
            'teazers': {
                'include': self.incl_teazers.get(),
                'titles': self.teaszers_selection.get_chosen_values()
            },
            'fingering-chart': {
                'include': self.incl_fingering.get(),
                'titles': self.fingering_chart_selection.get_chosen_values()
            }
        }