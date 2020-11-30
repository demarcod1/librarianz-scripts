from gui.util.util import validate_numerical_entry
from gui.screens.options.util.font_select import FontSelect
from tkinter import *
from tkinter import ttk

class PagesOptions(ttk.Frame):

    def __init__(self, parent, options, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        # Add enumeration font selection
        self.enumeration_font = FontSelect(self, 2,
                                            title='Chart Enumeration Font',
                                            middleLabel='Font',
                                            middleEntry=options['page-num-font']['name'],
                                            rightLabel='Size',
                                            rightEntry=options['page-num-font']['size'])
        self.enumeration_font.grid(row=0, column=0, sticky=(N, E, S, W), padx=20, pady=10)

        # Add enumeration toggle
        enum_frame = ttk.LabelFrame(self, text='Enumerate All Chart Files')

        self.enumerate = BooleanVar()
        self.enumerate.set(options['enumerate-pages'])
        enum_check = ttk.Checkbutton(enum_frame, text='Enumerate All Chartz', variable=self.enumerate)
        enum_check.grid(row=0, column=0, padx=10, pady=5)

        enum_frame.rowconfigure(0, weight='1')
        enum_frame.columnconfigure(0, weight='1')
        enum_frame.grid(row=0, column=1, sticky=(N, S, E, W), padx=20, pady=10)

        # Add width/height selectors
        page_dim_frame = ttk.Labelframe(self, text='Specify Page Dimensions (in Inches)')
        validate_fn = (page_dim_frame.register(validate_numerical_entry(True)), '%P')

        self.page_width = StringVar()
        self.page_width.set(options['page-size']['width'])
        width_label = ttk.Label(page_dim_frame, text='Width:')
        width_label.grid(row=0, column=0, sticky=E, padx=2, pady=5)
        width_spinbox = ttk.Spinbox(page_dim_frame, from_=0.0, to=20.0, increment=0.1, textvariable=self.page_width, validate='key', validatecommand=validate_fn)
        width_spinbox.grid(row=0, column=1, sticky=W, padx=2, pady=5)
        width_spinbox.bind('<FocusOut>', lambda _: self.page_width.set(options['page-size']['width']) if not len(self.page_width.get()) else '')

        self.page_height = StringVar()
        self.page_height.set(options['page-size']['height'])
        height_label = ttk.Label(page_dim_frame, text='Height:')
        height_label.grid(row=0, column=2, sticky=E, padx=2, pady=5)
        height_spinbox = ttk.Spinbox(page_dim_frame, from_=0.0, to=20.0, increment=0.1, textvariable=self.page_height, validate='key', validatecommand=validate_fn)
        height_spinbox.grid(row=0, column=3, sticky=W, padx=2, pady=5)
        height_spinbox.bind('<FocusOut>', lambda _: self.page_width.set(options['page-size']['height']) if not len(self.page_height.get()) else '')

        page_dim_frame.bind('<Button-1>', lambda e: e.widget.focus_set())
        page_dim_frame.rowconfigure(0, weight='1')
        for col in range(4):
            page_dim_frame.columnconfigure(col, weight='1')
        page_dim_frame.grid(row=1, column=0, columnspan=2, sticky=(N, E, S, W), padx=20, pady=10)


        # Make Resizeable
        for i in (0, 1):
            self.rowconfigure(i, weight='1')
            self.columnconfigure(i, weight='1')

    def get_page_options(self):
        _, font, size = self.enumeration_font.get_font_select()
        return {
            'enumerate-pages': self.enumerate.get(),
            'page-num-font': {
                'name': font,
                'size': size
            },
            'page-size': {
                'width': float(self.page_width.get()),
                'height': float(self.page_height.get())
            }
        }