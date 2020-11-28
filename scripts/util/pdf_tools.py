import json, os, glob
from . import util
from PyPDF2 import PdfFileReader, PdfFileMerger
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

# Adds the page number (or any arbitrary text) to the chart pdf file
def add_page_num(page, text: str, options):
    # Get page num information
    width, height = (inch * options["page-size"]["width"], inch * options["page-size"]["height"])
    font, size = (options["page-num-font"]["name"], options["page-num-font"]["size"])
    path = os.path.join(options["folder-dir"], "tmp", "page_num.pdf")

    # Draw text on canvas
    page_num = canvas.Canvas(path, pagesize=(width, height))
    page_num.setFont(font, size)
    page_num.drawCentredString(1.5 * inch, height - (.02 * size * inch), text)
    page_num.showPage()
    page_num.save()

    # Add page number to existing page
    with open(path, 'rb') as f:
        page_num = PdfFileReader(f).getPage(0)
        page.mergePage(page_num)
    return page

# Splits the raw list of parts files into lists of Lettered, Numbered, fingering chart
def categorize_parts(title_map, options):
    lettered, numbered, special = [], [], { "fingering_chart": [], "teazers": [] }
    for title in title_map:
        # parse filename
        file = title_map[title]

        # check to see if it's a fingering chart
        if options["fingering-chart"]["include"] and title in options["fingering-chart"]["titles"]:
            special["fingering_chart"].append(file)
        
        # check to see if it's a teazer
        elif options["teazers"]["include"] and title in options["teazers"]["titles"]:
            special["teazers"].append(file)
        
        # check to see if it's a lettered chart
        elif title in options["lettered-chartz"]:
            lettered.append(file)

        # by default, it's a numbered chart
        else:
            numbered.append(file)

    for list in (lettered, numbered, special["teazers"]):
        enforceRules(list, options["enforce-order"], title_map)

    return lettered, numbered, special

# Downloads all the files from a Separated Section Parts folder
def download_part_files(service, curr_parts_id, part, dir, verbose=False):
    # Retrieve files
    folders = util.get_drive_files(service, curr_parts_id, files_only=False, name=part)
    if not folders or len(folders) != 1:
        print(f'WARNING: Unable to find folder "{part}"')
        return
    files = util.get_drive_files(service, folders[0].get("id"), file_types=[".pdf"], is_shortcut=True)
    if not files or len(files) == 0:
        print(f'WARNING: Could not find any part files for "{part}"')
        return
    
    # Validate target directory
    path = os.path.join(dir, part)
    validate_dir(path, verbose)

    # Delete all existing files in that directory
    to_delete = glob.glob(f'{path}/*')
    for f in to_delete:
        os.remove(f)
    
    # Download files
    for file in files:
        # print(file)
        util.download_file(service, file["shortcutDetails"]["targetId"], path, file.get("name"), verbose)

# Enforce ordering rules
def enforceRules(list, rules, title_map):
    for rule in rules:
        # verify first chart
        first = title_map.get(rule[0])
        if not first in list: continue

        # find later chartz
        later_chartz = []
        for i in range(1, len(rule)):
            chart = title_map.get(rule[i])
            if not chart in list: continue
            later_chartz.append(chart)
            list.remove(chart)
        later_chartz.reverse()

        # Reorder according to rule
        first_pos = list.index(first)
        for chart in later_chartz:
            list.insert(first_pos + 1, chart)

# Enumerates all the pdf documents, returning a list of pages
# style: 0 = numbers, 1 = Letters, parts_map: will be modified to include mapping from counter -> file
# write_pages: true if you wish to return a bunch of pages, false if you only want mappings
def enumerate_pages(files, options, style=0, start=None, page_map=None, write_pages=False):
    pages = []
    if start == None:
        start = 1 if style == 0 else 'A'
    counter = start

    for file in files:
        try:         
            # Save page num assignment to map
            if page_map != None: page_map[counter] = file

            # Exit iteration if we don't wish to assemble pages
            if not write_pages:
                counter = (counter + 1) if style == 0 else (chr(ord(counter) + 1))
                continue

            # Read input file
            input = PdfFileReader(open(file, 'rb'))
            num_pages = input.getNumPages()
            page_num = f'{counter}'

            # Add all the pages to the list
            for i in range(num_pages):
                input_page = input.getPage(i)
                if num_pages > 1: page_num = f'{counter}.{i + 1}'
                pages.append(add_page_num(input_page, page_num, options) if options["enumerate-pages"] else input_page)
        except:
            print(f'Error when parsing "{file}"')
        
        # Increment Counter
        counter = (counter + 1) if style == 0 else (chr(ord(counter) + 1))

    return pages

# Generates the song files for a folder, returning a list of pages
# If write_pages is false, it will populate maps but not write any actual pages
def generate_parts_pages(title_map, toc_maps, options, write_pages=False):
    output = []
    lettered, numbered, special = categorize_parts(title_map, options)

    # Fingering chart
    if write_pages and len(special["fingering_chart"]):
        output.extend(to_pages(special["fingering_chart"][0]))

    # Lettered chartz
    output.extend(enumerate_pages(lettered, options, style=1, page_map=toc_maps[0], write_pages=write_pages))

    # Numbered chartz
    output.extend(enumerate_pages(numbered, options, page_map=toc_maps[1], write_pages=write_pages))

    # Teazers
    if len(special["teazers"]):
        output.extend(enumerate_pages(special["teazers"], options, style=1, start='a', page_map=toc_maps[2], write_pages=write_pages))
    
    return output

# Generates the table of contents file
def generate_toc(toc_maps, options, file, verbose=False):
    # Get page num information
    width, height = (inch * options["page-size"]["width"], inch * options["page-size"]["height"])
    path = os.path.dirname(file)
    validate_dir(path, verbose)
    
    # Generate toc doc and data
    toc = SimpleDocTemplate(file, pagesize=(width, height),
                            leftMargin=inch * .5, rightMargin=inch * .5,
                            topMargin=.75 * inch, bottomMargin=inch*.25)
    styles = generate_toc_styles(options)
    data = generate_toc_data(toc_maps, options, styles)

    # Construct table
    table = Table(data)
    table.setStyle(TableStyle([
        ('RIGHTPADDING', (0,0), (-1,-1), -3),
        ('LEFTPADDING', (0,0), (-1,-1), -3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0)
    ]))

    # Add title and footer
    def onFirstPage(canvas: canvas.Canvas, doc):
        canvas.saveState()
        font, size = (options["toc"]["title"]["font"], options["toc"]["title"]["size"])
        canvas.setFont(font, size)
        canvas.drawCentredString(width / 2, height - (.02 * inch * size), options["toc"]["title"]["label"])
        font, size = (options["toc"]["footer"]["font"], options["toc"]["footer"]["size"])
        canvas.setFont(font, size)
        canvas.drawCentredString(width / 2, (.02 * inch * size), options["toc"]["footer"]["label"])
        canvas.restoreState()

    # write the document to disk
    toc.build([table], onFirstPage=onFirstPage)
    if verbose: print(f'Successfully created table of contents file at "{file}"')

# Generates the data in the proper form
def generate_toc_data(toc_maps, options, styles):
    # Make a list of all the chartz, in lettered -> numbered -> teazers order
    raw_list = [] # list of title in toc + dollie
    for map in toc_maps:
        if not map: continue
        for key, val in map.items():
            title, _, _ = util.parse_file(os.path.basename(val))
            # Case insensitive match
            raw_list.append((f'{key}: {title}', 0 + (title in options["dollie-songs"])))
        raw_list.append(("", False))
    if len(raw_list) > 0: del raw_list[-1]

    # Refactor the data into table format
    data = []
    num_cols = options["toc"]["num-cols"]
    num_rows = -(len(raw_list) // -num_cols)
    for i in range(num_rows):
        row = []
        for j in range(num_cols):
            index = (num_rows * j) + i
            text, style = ("", styles[0]) if index >= len(raw_list) else (raw_list[index][0], styles[raw_list[index][1]])
            row.append(Paragraph(text=text, style=style))
        data.append(row)

    return data

# Generates the paragraph styles from the toc
def generate_toc_styles(options):
    # Non-dollie songs
    style_normal = ParagraphStyle("toc_normal",
                            fontName=options["toc"]["entry"]["font-normal"],
                            fontSize=options["toc"]["entry"]["size"],
                            alignment=0)
    
    # Dollie songs
    style_dollie = ParagraphStyle("toc_dollie",
                            fontName=options["toc"]["entry"]["font-dollie"],
                            fontSize=options["toc"]["entry"]["size"],
                            alignment=0)

    return style_normal, style_dollie

# This merges files of the same chart together and outputs a map from chartname -> filename
def process_files(files):
    title_map = {}
    for file in files:
        # parse filename
        title, _, _ = util.parse_file(os.path.basename(file))

        # if not already seen, add this file to the map
        if title not in title_map:
            title_map[title] = file
            continue

        # we need to merge pdfs into 1
        merger = PdfFileMerger()
        merger.append(PdfFileReader(open(title_map[title], "rb")))
        merger.append(PdfFileReader(open(file, "rb")))
        merger.write(title_map[title])
        os.remove(file)

    return title_map

# Converts a pdf file into a list of pages
def to_pages(file):
    file_in = PdfFileReader(file)
    return file_in.pages

# Validates the existence of a directory, creating it if need be
def validate_dir(path, verbose=False):
    if not os.path.exists(path):
        os.makedirs(path)
        if verbose: print(f'DEBUG: Making directory "{path}"')

# Validates that a part's files are properly formatted
def validate_part(part, options):
    path = os.path.join(options["folder-dir"], "parts", part)
    if not os.path.exists(path):
        print(f'WARNING: Path to files for part "{part}" does not exist')
    
    # Validate titles
    title_map = process_files(sorted(glob.glob(f'{path}/*.pdf')))
    if len(title_map.keys()) == 0:
        print(f'WARNING: No files found for part "{part}", folder will not be generated')
        return None
    validate_titles(title_map, options, "scripts/options/folder_creator_options.json", verbose=options["verbose"])

    return title_map

# Validate and update the lists of files in the options list
def validate_titles(title_map, options, update_path=None, verbose=False):
    titles = title_map.keys()
    
    # Helper method to find case-insensitive match
    def find_match(song: str):
        song_lower = song.lower()
        for title in titles:
            if song_lower == title.lower():
                if verbose: print(f'DEBUG: Found match for song "{song}": "{title}".')
                return title

    # Go through all the file lists and make repairs if necessary
    for i, song in enumerate(options["dollie-songs"]):
        if not song in titles:
            if update_path:
                match = find_match(song)
                if match: options["dollie-songs"][i] = match
                elif verbose: print(f'WARNING: Song "{song}" specified in "dollie-songs" was not found.')
    
    for i, song in enumerate(options["lettered-chartz"]):
        if not song in titles:            
            if update_path:
                match = find_match(song)
                if match: options["lettered-chartz"][i] = match
                elif verbose: print(f'WARNING: Song "{song}" specified in "lettered-chartz" was not found.')
    
    for i, rule in enumerate(options["enforce-order"]):
        for j, song in enumerate(rule):
            if not song in titles:
                if update_path:
                    match = find_match(song)
                    if match: options["enforce-order"][i][j] = match
                    elif verbose: print(f'WARNING: Song "{song}" specified in "enforce-order" was not found.')
    
    if update_path:
        with open(update_path, 'w') as f:
            json.dump(options, f, indent=4)
