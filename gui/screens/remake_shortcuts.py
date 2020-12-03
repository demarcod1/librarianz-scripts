from scripts.remake_shortcuts import remake_shortcuts
from gui.util.script_progress import ScriptProgress
from gui.util.multiselect import Multiselect
from gui.util.custom_text import CustomText
from gui.util.util import bind_button
from scripts.util.util import parse_options, write_options
from tkinter import *
from tkinter import ttk, messagebox

class RemakeShortcutsScreen(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.options = parse_options('parts.json')
        self.DELIMETERS = (":", "|")
        parts_frame = ttk.Labelframe(self, text='Configure Part Mappings')

        # Add info label
        info = ttk.Label(parts_frame, justify='center', text=f'Each line of text is a part alias configuration.\nThe part name is followed by "{self.DELIMETERS[0]}", and aliases are delimited by "{self.DELIMETERS[1]}".\nFor example, if you wish for files "All Right Now - Toobz" and\n"All Right Now - Tööbz" to be mapped to the same folder,\nyou would enter "Toobz{self.DELIMETERS[0]} Toobz {self.DELIMETERS[1]} Tööbz"')
        info.grid(row=0, column=0, padx=10, pady=5)

        # Add text input area
        dummy_frame = ttk.Frame(parts_frame)

        self.parts_text = CustomText(dummy_frame, width=70, height=15, wrap='none', font=('TkDefaultFont', '10'), undo=True)
        self.parts_text.grid(row=0, column=0, sticky=(N, E, S, W))
        self.parts_text.tag_configure('delimeter-0-good', font=('Courier', '10', 'bold'), foreground='green')
        self.parts_text.tag_configure('delimeter-0-bad', font=('Courier', '10', 'bold'), foreground='red')
        self.parts_text.tag_configure('delimeter-1-good', font=('Courier', '10', 'bold'), foreground='blue')
        self.parts_text.tag_configure('delimeter-1-bad', font=('Courier', '10', 'bold'), foreground='red')
        self.parts_text.bind('<<TextModified>>', self.tag_delimeters)

        scrollx = ttk.Scrollbar(dummy_frame, orient='horizontal', command=self.parts_text.xview)
        scrolly = ttk.Scrollbar(dummy_frame, orient='vertical', command=self.parts_text.yview)
        self.parts_text['xscrollcommand'] = scrollx.set
        self.parts_text['yscrollcommand'] = scrolly.set
        scrollx.grid(row=1, column=0, sticky=(E, W, N))
        scrolly.grid(row=0, column=1, sticky=(N, S, W))

        parts_frame.grid(row=0, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)

        dummy_frame.grid(row=1, column=0, sticky=(N, E, S, W), padx=10, pady=5)
        dummy_frame.rowconfigure(0, weight='1')
        dummy_frame.columnconfigure(0, weight='1')

        # Populate text
        self.populate_parts(self.options['parts'])

        # Make Text Area Resizeable
        parts_frame.columnconfigure(0, weight='1')
        parts_frame.rowconfigure(1, weight='1')


        # Add exclusion selection
        self.exclusions = Multiselect(self, input=self.options['exclude'],
                                        title='Parts to Exclude from Live Digital Library',
                                        header='Part Name',
                                        addText='Add Part',
                                        warn=True,
                                        height=5)
        self.exclusions.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky=(N, E, S, W))

        # Run script/Close buttons
        close_button = ttk.Button(self, text='Close', command=lambda: parent.master.destroy())
        bind_button(close_button)
        run_script_button = ttk.Button(self, text='Remake Shortcuts', command=self.run_script)
        bind_button(run_script_button)

        close_button.grid(row=2, column=0, sticky=(S, W), padx=20, pady=10)
        run_script_button.grid(row=2, column=1, sticky=(S, E), padx=20, pady=10)

        # Allow resizing
        self.rowconfigure(0, weight="1")
        self.rowconfigure(1, weight="1")
        self.columnconfigure(1, weight="1")
    
    # Logic that runs the script. It will prompt the user with a warning dialogue before allowing them to run
    def run_script(self):
        # Get part options
        self.options['parts'] = { part.strip(): [ alias.strip() for alias in aliases.split(self.DELIMETERS[1]) if alias.strip() ] for part, aliases in [tuple(line.split(self.DELIMETERS[0])) for line in self.parts_text.get('1.0', 'end').strip().splitlines() if len(line.split(self.DELIMETERS[0])) == 2 ] }
        self.options['exclude'] = self.exclusions.get_chosen_values()
        write_options(self.options, "parts.json")

        # Prompt user to confirm action
        if not messagebox.askyesno('Confirm Remaking Shortcuts', 'Are you sure you want to remake all Digital Library shortcuts? This script may take 30 mins to complete, and will require manual removal of excess folders if aborted mid-run. Live Digital Library users may be affected after this script completes, as old folders will be deleted just before the script terminates.', icon='warning', default='no'):
            return

        # Re-show main window
        def callback(code):
            self.master.master.deiconify()
            print(f"Thread Finished with code {code}")
        

        ScriptProgress(self, script=remake_shortcuts, callback=callback, title="Remaking Shortcuts (This may take 20-40 mins)", name="Remake Shortcuts", safe=True)
        self.master.master.withdraw()
    
    # Populates the text area with the rules
    def populate_parts(self, parts_dict):
        str = ''
        for part, aliases in parts_dict.items():
            str += f'{part}{self.DELIMETERS[0]} '
            for i, alias in enumerate(aliases):
                str += alias
                if i < len(aliases) - 1:
                    str += f' {self.DELIMETERS[1]} '
                else:
                    str += '\n'
        self.parts_text.insert('end', str)

    # Applies tags to all the delimeters seen
    def tag_delimeters(self, *args):
        del_lengths = [len(self.DELIMETERS[index]) for index in (0, 1)]
        # Remove invalid tags
        for index in (0, 1):
            for tag in (f'delimeter-{index}-good', f'delimeter-{index}-bad'):
                ranges = self.parts_text.tag_ranges(tag)
                for i in range(0, len(ranges), 2):
                    if self.parts_text.get(ranges[i], ranges[i+1]) != del_lengths[index]:
                        self.parts_text.tag_remove(tag, ranges[i], ranges[i+1])
        
        # Add new tags
        for index in (0, 1):
            start_index = '1.0'
            while True:
                start_index = self.parts_text.search(self.DELIMETERS[index], start_index, 'end', exact=True)
                if not start_index:
                    break
                if (self.parts_text.get(start_index + 'linestart', start_index).strip() and self.parts_text.get(start_index+f'+{del_lengths[index]}c', start_index + 'lineend').strip() and (index == 1 or not self.DELIMETERS[0] in self.parts_text.get(start_index + 'linestart', start_index))):
                    self.parts_text.tag_remove(f'delimeter-{index}-bad', start_index, start_index+f'+{del_lengths[index]}c')
                    self.parts_text.tag_add(f'delimeter-{index}-good', start_index, start_index+f'+{del_lengths[index]}c')
                else:
                    self.parts_text.tag_remove(f'delimeter-{index}-good', start_index, start_index+f'+{del_lengths[index]}c')
                    self.parts_text.tag_add(f'delimeter-{index}-bad', start_index, start_index+f'+{del_lengths[index]}c')
                start_index += '+1c'
    
