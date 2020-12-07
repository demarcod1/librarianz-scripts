from gui.util.multiselect import Multiselect
from gui.util.custom_text import CustomText
from tkinter import *
from tkinter import ttk

class RulesOptions(ttk.Frame):
    def __init__(self, parent, options, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.DELIMETER = '->'
        rules_frame = ttk.Labelframe(self, text='Add Ordering Rules')

        # Add info label
        info = ttk.Label(rules_frame, justify='center', text=f'Each line of text corresponds to a special ordering of chartz\nUse "{self.DELIMETER}" as a delimeter between chart names\nExample Rule: Foreplay -> Knights of Cydonia')
        info.grid(row=0, column=0, padx=10, pady=5)

        # Add text input area
        dummy_frame = ttk.Frame(rules_frame)

        self.rules_text = CustomText(dummy_frame, width=70, height=5, wrap='none', font=('TkDefaultFont'))
        self.rules_text.grid(row=0, column=0, sticky=(N, E, S, W))
        self.rules_text.tag_configure('delimeter-good', font=('TkFixedFont'), foreground='green')
        self.rules_text.tag_configure('delimeter-bad', font=('TkFixedFont'), foreground='red')
        self.rules_text.bind('<<TextModified>>', self.tag_delimeter)

        scrollx = ttk.Scrollbar(dummy_frame, orient='horizontal', command=self.rules_text.xview)
        scrolly = ttk.Scrollbar(dummy_frame, orient='vertical', command=self.rules_text.yview)
        self.rules_text['xscrollcommand'] = scrollx.set
        self.rules_text['yscrollcommand'] = scrolly.set
        scrollx.grid(row=1, column=0, sticky=(E, W, N))
        scrolly.grid(row=0, column=1, sticky=(N, S, W))

        rules_frame.grid(row=0, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        dummy_frame.grid(row=1, column=0, sticky=(N, E, S, W), padx=10, pady=5)
        dummy_frame.rowconfigure(0, weight='1')
        dummy_frame.columnconfigure(0, weight='1')

        # Add exclusion list
        self.exclusion_list = Multiselect(self, options['exclude-songs'],
                                        title='Exclude Chartz from Folders',
                                        header='Chart Name',
                                        addText='Add Chart',
                                        warn=False,
                                        orient='vertical',
                                        height=5)
        self.exclusion_list.grid(row=1, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        # Make Resizeable
        rules_frame.columnconfigure(0, weight='1')
        rules_frame.rowconfigure(0, weight='1')
        rules_frame.rowconfigure(1, weight='1')
        self.columnconfigure(0, weight='1')
        self.rowconfigure(0, weight='1')

        # Populate rules
        self.populate_rules(options['enforce-order'])
    
    def populate_rules(self, rules):
        str = ''
        for i, rule in enumerate(rules):
            for j, chart in enumerate(rule):
                str += chart
                if (j < len(rule) - 1):
                    str += f' {self.DELIMETER} '
                else:
                    str += '\n'
        self.rules_text.insert('end', str)
    
    def tag_delimeter(self, *args):
        # Remove invalid tags
        for tag in ('delimeter-good', 'delimeter-bad'):
            ranges = self.rules_text.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                if self.rules_text.get(ranges[i], ranges[i+1]) != self.DELIMETER:
                    self.rules_text.tag_remove(tag, ranges[i], ranges[i+1])

        # Apply tags
        start_index = '1.0'
        while True:
            start_index = self.rules_text.search(self.DELIMETER, start_index, 'end', exact=True)
            if not start_index:
                break
            if (self.rules_text.get(start_index + 'linestart', start_index).strip() and self.rules_text.get(start_index+f'+{len(self.DELIMETER)}c', start_index + 'lineend').strip()):
                self.rules_text.tag_remove('delimeter-bad', start_index, start_index+f'+{len(self.DELIMETER)}c')
                self.rules_text.tag_add('delimeter-good', start_index, start_index+f'+{len(self.DELIMETER)}c')
            else:
                self.rules_text.tag_remove('delimeter-good', start_index, start_index+f'+{len(self.DELIMETER)}c')
                self.rules_text.tag_add('delimeter-bad', start_index, start_index+f'+{len(self.DELIMETER)}c')
            start_index += '+1c'
    
    def get_rule_options(self):
        return { "enforce-order": [ [ chart.strip() for chart in rule.split(self.DELIMETER) ] for rule in self.rules_text.get('1.0', 'end').strip().splitlines() ], "exclude-songs": self.exclusion_list.get_chosen_values() }

