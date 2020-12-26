import os
from gui.util.util import bind_button
from tkinter import *
from tkinter import ttk, messagebox

class OrderSelect(ttk.LabelFrame):

    def __init__(self, parent, options, pathfn, *args, **kwargs):
        # Initialize superclass
        title = kwargs.get("title") or "Filler Ordering"
        relief = kwargs.get("relief") or "solid"
        self.pathfn = pathfn

        ttk.Labelframe.__init__(self, parent, text=title, relief=relief)

        # Set path and current list of filler
        self.path = options['filler']['directory']
        self.list = options['filler']['order']

        # Create main treeview
        treeview_frame = ttk.Frame(self)

        self.tree = ttk.Treeview(treeview_frame, height=kwargs.get("height") or 8)
        self.tree.heading('#0', text=kwargs.get("heading") or "Filler Order")
        self.tree.column('#0', stretch=YES)
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.tree_selection_changed())
        self.bind('<Button-1>', self.clear_selection)
        self.tree.grid(row=0, column=0, stick=(N, E, S, W))

        scrolly = ttk.Scrollbar(treeview_frame, orient='vertical', command=self.tree.yview)
        self.tree['yscrollcommand'] = scrolly.set
        scrolly.grid(row=0, column=1, sticky=(N, S, E, W))

        treeview_frame.columnconfigure(0, weight='1')
        treeview_frame.rowconfigure(0, weight='1')

        treeview_frame.grid(row=0, column=0, padx=10, pady=5, sticky=(N, E, S, W))
        self.rowconfigure(0, weight='1')
        for i in range(2):
            self.columnconfigure(0, weight='1')
        
        # Create up, down, and refresh buttons
        button_frame = ttk.Frame(self)

        self.up = ttk.Button(button_frame, text='Move Up', command=self.move_up)
        self.up.state(["disabled"])
        bind_button(self.up)

        self.down = ttk.Button(button_frame, text='Move Down', command=self.move_down)
        self.down.state(["disabled"])
        bind_button(self.down)

        self.refresh = ttk.Button(button_frame, text='Refresh', command=self.refresh)
        bind_button(self.refresh)

        self.up.grid(row=0, column=0, padx=10, pady=5, sticky=S)
        self.refresh.grid(row=1, column=0, padx=10, pady=5)
        self.down.grid(row=2, column=0, padx=10, pady=5, sticky=N)

        for i in range(3):
            button_frame.rowconfigure(i, weight='1')
        button_frame.columnconfigure(0, weight='1')

        button_frame.grid(row=0, column=1, sticky=(N, E, S, W), padx=10, pady=5)

        # Initialize tree
        self.add_list_to_tree(options['filler']['order'])

    # Returns the ordered list
    def get_ordered_list(self):
        return [self.tree.item(k)['text'] for k in self.tree.get_children('')]
    
    # Trigger if the tree's selection changed
    def tree_selection_changed(self, *args):
        selection = self.tree.selection()
        children = self.tree.get_children()
        enable_up = False
        for item in selection:
            if item not in children[:len(selection)]:
                enable_up = True
                break
        self.up.state([f'{"!" if enable_up else ""}disabled'])
        
        enable_down = False
        for item in selection:
            if item not in children[-len(selection):]:
                enable_down = True
                self.down.state(["!disabled"])
                break
        self.down.state([f'{"!" if enable_down else ""}disabled'])
    
    # Clears the selected tree elements
    def clear_selection(self, *args):
        for item in self.tree.selection():
            self.tree.selection_remove(item)
    
    # Moves the selected elements up
    def move_up(self, *args):
        selection = self.tree.selection()
        for item in selection:
            self.tree.move(item, '', self.tree.index(item) - 1)
        self.tree_selection_changed()

    # Moves the selected elements down
    def move_down(self, *args):
        selection = self.tree.selection()
        for item in reversed(selection):
            self.tree.move(item, '', self.tree.index(item) + 1)
        self.tree_selection_changed()

    # Refreshes the order table by reading from selected directory
    def refresh(self, *args):
        if len(self.tree.get_children('')) > 2 and not messagebox.askyesno(title="Refresh Filler Order", message="Are you sure you wish to refresh the filler order?"): return
        new_list = []
        for filename in os.listdir(self.pathfn()):
            basename, extension = os.path.splitext(filename)
            if extension == ".pdf":
                new_list.append(basename)
        self.add_list_to_tree(new_list)


    # Populates the tree with the contents of a list, removing any old elements
    def add_list_to_tree(self, list):
        self.tree.delete(*self.tree.get_children(''))
        for entry in list:
            self.tree.insert('', index='end', text=entry)