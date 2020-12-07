from gui.util.util import bind_button
from tkinter import *
from tkinter import ttk, messagebox

class Multiselect(ttk.Labelframe):

    def __init__(self, parent, input, *args, **kwargs):
        # Initialize superclass
        title = kwargs.get("title") or "Select Items"
        relief = kwargs.get("relief") or "solid"

        ttk.Labelframe.__init__(self, parent, text=title, relief=relief)

        # Initialize treeview list
        key1 = kwargs.get('key1')
        key2 = kwargs.get('key2')

        names = []
        locs = []
        if not key1 or not key2:
            names = input
        else:
            names = [ item[key1] for item in input ]
            locs = [ item[key2] for item in input ]
        
        left_col = kwargs.get("header") or "Item"
        self.right_col = ['Destination'] if key1 and key2 else []

        # Define treeview
        treeview_frame = ttk.Frame(self)

        self.reverse = False
        self.tree = ttk.Treeview(treeview_frame, columns=self.right_col, height=kwargs.get("height") or 5)
        self.tree.heading('#0', text=left_col, command=lambda: self.tree_sort())
        self.tree.column('#0', stretch=YES)
        if len(self.right_col) > 0:
            self.tree.heading('#1', text=self.right_col[0])
            self.tree.column('#1', stretch=YES, width=80)
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.tree_selection_changed())
        self.tree.bind('<Control-a>', self.select_all)
        self.bind('<Button-1>', self.clear_selection)
        self.tree.grid(row=0, column=0, stick=(N, E, S, W))

        scrolly = ttk.Scrollbar(treeview_frame, orient='vertical', command=self.tree.yview)
        self.tree['yscrollcommand'] = scrolly.set
        scrolly.grid(row=0, column=1, sticky=(N, S, E, W))

        treeview_frame.columnconfigure(0, weight='1')
        treeview_frame.rowconfigure(0, weight='1')

        # New item entry
        self.entry_text = StringVar()
        entry = ttk.Entry(self, textvariable=self.entry_text)
        self.entry_text.trace_add('write', self.entry_changed)

        # Add item entry
        add_text = kwargs.get("addText") or 'Add Item'
        self.add_entry = ttk.Button(self, text=add_text, command=self.add_item_cmd)
        self.add_entry.state(["disabled"])
        bind_button(self.add_entry)
        entry.bind("<Return>", lambda e: self.add_entry.invoke())
        entry.bind("<KP_Enter>", lambda e: self.add_entry.invoke())

        
        # Select destination radio buttons
        self.destination = None
        select_dest_frame = None
        if len(self.right_col) > 0:
            select_dest_frame = ttk.Frame(self)
            self.destination = IntVar()
            self.destination.set(0)

            current_chartz = ttk.Radiobutton(select_dest_frame, text='Current Chartz', variable=self.destination, value=0)
            old_chartz = ttk.Radiobutton(select_dest_frame, text='Old Chartz', variable=self.destination, value=1)
            future_chartz = ttk.Radiobutton(select_dest_frame, text='Future Chartz', variable=self.destination, value=2)


            current_chartz.grid(row=0, column=0, sticky=(N, S))
            old_chartz.grid(row=0, column=1, sticky=(N, S))
            future_chartz.grid(row=0, column=2, sticky=(N, S))

            if kwargs.get("archive"):
                archive = ttk.Radiobutton(select_dest_frame, text='Archive', variable=self.destination, value=3)
                archive.grid(row=0, column=3, sticky=(N, S))

            for i in range(4):
                select_dest_frame.columnconfigure(i, weight="1")

        
        # Delete selection/all buttons
        self.del_sel = ttk.Button(self, text='Delete Selection', command=self.delete_selection)
        self.del_sel.state(['disabled'])
        bind_button(self.del_sel)

        self.warn_before_deleting = kwargs.get('warn')
        self.del_all = ttk.Button(self, text='Delete All', command=self.delete_all)
        self.del_all.state(['disabled'])
        bind_button(self.del_all)

                
        # Add items to treeview
        for i in range(len(names)):
            loc = locs[i] if i < len(locs) else None
            self.insert_data(names[i], loc)
        self.tree_sort(False)

        # Grid the items/handle orientation
        if kwargs.get('orient') == 'vertical':
            sel_dest_enabled = select_dest_frame != None
            
            entry.grid(row=0, column=0, padx=10, pady=2, sticky=E)
            self.add_entry.grid(row=0, column=1, padx=2, pady=5, sticky=W)
            if sel_dest_enabled: select_dest_frame.grid(row=1, column=0, columnspan=2, sticky=N, padx=10, pady=5)

            treeview_frame.grid(row=1 + sel_dest_enabled, column=0, columnspan=2, padx=10, pady=5, sticky=(N, S, E, W))

            self.del_sel.grid(row=2 + sel_dest_enabled, column=0, sticky=W, padx=10, pady=5)
            self.del_all.grid(row=2 + sel_dest_enabled, column=1, sticky=E, padx=10, pady=5)

            # Resize rows/columns
            self.columnconfigure(0, weight='1')
            self.columnconfigure(1, weight='1')
            for i in range(3 + sel_dest_enabled):
                self.rowconfigure(i, weight='1')
        else:
            treeview_frame.grid(row=0, column=0, rowspan=3, padx=10, pady=5, sticky=(N, E, S, W))

            entry.grid(row=0, column=1, padx=10, pady=5, sticky=(W, E, S))
            self.add_entry.grid(row=0, column=2, sticky=(E, W, S), padx=10, pady=5)
            if (select_dest_frame != None): select_dest_frame.grid(row=1, column=1, columnspan=2, sticky=(N, E, W), padx=10, pady=5)

            self.del_sel.grid(row=2, column=1, sticky=(N, E, W), padx=10, pady=5)
            self.del_all.grid(row=2, column=2, sticky=(N, E, W), padx=10, pady=5)

            # Resize rows, cols
            for i in range(3):
                self.rowconfigure(i, weight="1")
                self.columnconfigure(i, weight="1")

    # Get the chosen values (all items from the tree)
    def get_chosen_values(self, key1=None, key2=None):
        dest_to_num = lambda dest: 0 if dest == "Current" else 1 if dest == "Old" else 2 if dest == "Future" else 3
        if len(self.right_col) > 0:
            return [{ key1: val1, key2: dest_to_num(val2)} for (val1, val2) in [(self.tree.item(k)['text'], self.tree.item(k)['values'][0]) for k in self.tree.get_children('')]]
        return [self.tree.item(k)['text'] for k in self.tree.get_children('')]

    # Sort the tree by item
    def tree_sort(self, change_order=True):
        # reverse sort if change_order is true
        self.reverse = self.reverse != change_order

        l = [(self.tree.item(k)['text'], k) for k in self.tree.get_children('')]
        l.sort(reverse=self.reverse)

        # rearrange items in sorted positions
        for index, (text, k) in enumerate(l):
            self.tree.move(k, '', index)

    # Trigger if the tree's selection changed
    def tree_selection_changed(self, *args):
        if len(self.tree.selection()):
            self.del_sel.state(['!disabled'])
        else:
            self.del_sel.state(['disabled'])

    # Trigger if the entry field changed
    def entry_changed(self, *args):
        if len(self.entry_text.get().strip()):
            self.add_entry.state(["!disabled"])
        else:
            self.add_entry.state(["disabled"])
    
    # Clears the selected tree elements
    def clear_selection(self, *args):
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        
    # Selects all items in the tree
    def select_all(self, *args):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    # Deletes all tree elements
    def delete_all(self, *args):
        self.select_all()
        self.delete_selection(all=True)
        self.clear_selection()

    # Deletes the selected tree elements
    def delete_selection(self, all=False, *args):
        selection = self.tree.selection()
        if (not self.warn_before_deleting and (len(selection) < 3 or len(self.tree.get_children('')) >= 2 * len(selection))) or messagebox.askyesno(parent=self, title=f'Delete {"All" if all else "Selection"}', message=f'Are you sure you want to remove {"all the" if all else "the selected"} entries?', icon='warning', default='no'):
            for item in selection:
                self.tree.delete(item)
            if not len(self.tree.get_children('')): self.del_all.state(['disabled'])
            self.del_sel.state(['disabled'])

    # Adds an item to the tree, in sorted order
    def add_item_cmd(self, *args):
        text = self.entry_text.get().strip()
        if len(text):
            self.insert_data(text, loc=self.destination if self.destination == None else self.destination.get())
            self.tree_sort(change_order=False)
            self.entry_text.set('')

    # Performs the actual insertion operation
    def insert_data(self, item, loc=None, index="end"):
        values = [] if loc == None else ["Current"] if loc == 0 else ["Old"] if loc == 1 else ["Future"] if loc == 2 else ["Archive"]
        self.tree.insert('', index=index, text=item, values=values)
        self.del_all.state(['!disabled'])



