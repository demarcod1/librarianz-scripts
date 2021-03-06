import io
import json, os, glob
from PyPDF2.generic import RectangleObject
from scripts.util.thread_events import check_stop_script, thread_print
from typing import List
from scripts.util.util import resourcePath

from PyPDF2.pdf import PageObject, PdfFileWriter, PdfFileReader
from scripts.util import util
from PyPDF2 import PdfFileMerger
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

# Create and return an array of pages, containing all the filler in the proper order
def add_filler(options):
    output = []
    filler_data = options['filler']
    if not filler_data["include"]: return []
    if not len(filler_data["order"]):
        thread_print("WARNING: No filler ordering was specified, filler will not be added")
        return []
    
    for filename in filler_data["order"]:
        try:
            filler = PdfFileReader(open(os.path.join(filler_data["directory"], f'{filename}.pdf'), 'rb'))
            for i in range(filler.getNumPages()):
                page: PageObject = filler.getPage(i)
                if not validate_mediabox(page.mediaBox, options):
                    thread_print(f'WARNING: Page {i + 1} in "{filename}" has incorrect dimensions\nExpected {options["page-size"]["width"]} x {options["page-size"]["height"]}, received {float(page.mediaBox.getWidth()) / inch} x {float(page.mediaBox.getHeight()) / inch}.')
                output.append(filler.getPage(i))
        except OSError:
            thread_print(f'WARNING: Unable to open file "{filename}.pdf", this item will be skipped.')
            continue
    return output
        
# Adds the page number (or any arbitrary text) to the chart pdf file
# Source: https://stackoverflow.com/questions/1180115/add-text-to-existing-pdf-using-python
def add_page_num(page, text: str, options):
    # Get page num information
    width, height = (inch * options["page-size"]["width"], inch * options["page-size"]["height"])
    font, size = (options["page-num-font"]["name"], options["page-num-font"]["size"])
    packet = io.BytesIO()

    # Draw text on canvas
    page_num = canvas.Canvas(packet, pagesize=(width, height))
    page_num.setFont(font, size)
    page_num.drawCentredString(1.5 * inch, height - (.02 * size * inch), text)
    page_num.save()

    # Add page number to existing page
    packet.seek(0)
    page_num_pdf = PdfFileReader(packet).getPage(0)       
    page_num_pdf.mergePage(page)

    return page_num_pdf


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

# Creates a temporary file of just page numbers
def create_page_number_file(page_num_list, options, filename='page_nums.pdf'):
    # Get page num information
    width, height = (inch * options["page-size"]["width"], inch * options["page-size"]["height"])
    font, size = (options["page-num-font"]["name"], options["page-num-font"]["size"])
    path = os.path.join(options["folder-dir"], "tmp", filename)

    # Set up canvas
    page_num_canvas = canvas.Canvas(path, pagesize=(width, height))

    for text in page_num_list:
        page_num_canvas.setFont(font, size)
        page_num_canvas.drawCentredString(1.5 * inch, height - (.02 * size * inch), text)
        page_num_canvas.showPage()
    page_num_canvas.save()

# Downloads all the files from a Separated Section Parts folder
def download_part_files(service, curr_parts_id, part, dir, verbose=False):
    # Retrieve files
    folders = util.get_drive_files(service, curr_parts_id, files_only=False, name=part)
    if not folders or len(folders) != 1:
        thread_print(f'ERROR: Unable to find folder "{part}"')
        return
    files = util.get_drive_files(service, folders[0].get("id"), file_types=[".pdf"], is_shortcut=True)
    if not files or len(files) == 0:
        thread_print(f'WARNING: Could not find any part files for "{part}"')
        return
    
    # Validate target directory
    check_stop_script()
    path = os.path.join(dir, part)
    validate_dir(path, verbose)

    # Delete all existing files in that directory
    to_delete = glob.glob(f'{path}/*')
    for f in to_delete:
        os.remove(f)
    
    # Download files
    for file in files:
        check_stop_script()
        util.download_file(service, file["shortcutDetails"]["targetId"], path, file.get("name"), verbose)
    
    # Print success
    thread_print(f'Successfully finished downloading part files for "{part}"')

# Enforce ordering rules
def enforceRules(list, rules, title_map):
    no_filler_before = []
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
        no_filler_before.extend(later_chartz)

        # Reorder according to rule
        first_pos = list.index(first)
        for chart in later_chartz:
            list.insert(first_pos + 1, chart)
    return no_filler_before

# Enumerates all the pdf documents, returning a list of pages
# style: 0 = numbers, 1 = Letters, parts_map: will be modified to include mapping from counter -> file
# page_map: dict of enumeration to file
# write_pages: true if you wish to return a bunch of pages, false if you only want mappings
# no_filler_before - a list of files that filler should not precede. If filler is not to be interlaced inbetween numbered chartz, this field should be None
def enumerate_pages(files, options, style=0, start=None, page_map=None, write_pages=False, no_filler_before=None, verbose=False):
    pages = []
    if start == None:
        start = 1 if style == 0 else 'A'
    counter = start

    # Read filler pages if filler needs to be interlaced
    filler = None
    if no_filler_before: filler = add_filler(options)
    valid_filler_indeces = []

    for file in files:
        check_stop_script()
        try:         
            # Save page num assignment to map
            if page_map != None: page_map[counter] = file
            if filler and file not in no_filler_before: valid_filler_indeces.append(len(pages))

            # Read input file
            input = PdfFileReader(open(file, 'rb'))
            num_pages = input.getNumPages()
            page_num = f'{counter}'

            # Add all the pages to the list
            for i in range(num_pages):
                input_page: PageObject = input.getPage(i)

                # Verify that it has the proper dimensions
                mediabox = input_page.mediaBox
                if not validate_mediabox(mediabox, options):
                    thread_print(f'WARNING: Page {i + 1} in "{file}" has incorrect dimensions\nExpected {options["page-size"]["width"]} x {options["page-size"]["height"]}, received {float(mediabox.getWidth()) / inch} x {float(mediabox.getHeight()) / inch}.')
                    continue

                # Calculate this page number
                if not write_pages: continue
                if num_pages > 1: page_num = f'{counter}.{i + 1}'
                pages.append(add_page_num(input_page, page_num, options) if options["enumerate-pages"] else input_page)

        except OSError:
            thread_print(f'Error when parsing "{file}"')
        
        # Increment Counter
        counter = (counter + 1) if style == 0 else (chr(ord(counter) + 1))

    # Interlace filler (if applicable)
    if filler: interlace_filler(pages, filler, valid_filler_indeces)

    return pages

# Generates the song files for a folder, returning a list of pages
# If write_pages is false, it will populate maps but not write any actual pages
def generate_parts_pages(title_map, toc_maps, options, part, write_pages=False, verbose=False):
    output = []
    filler_pos = options['filler']['position']
    lettered, numbered, special = categorize_parts(title_map, options)

    # Fingering chart
    if filler_pos == 0: output.extend(add_filler(options))
    if write_pages and len(special["fingering_chart"]):
        if verbose:
            thread_print(f'Writing fingering chart to {part} folder')
        output.extend(to_pages(special["fingering_chart"][0]))

    # Lettered chartz
    if verbose:
        thread_print(f'Writing lettered chartz to {part} folder')
    output.extend(enumerate_pages(lettered, options, style=1, page_map=toc_maps[0], write_pages=write_pages, verbose=verbose))
    if filler_pos == 1: output.extend(add_filler(options))

    # Numbered chartz
    if verbose:
        thread_print(f'Writing numbered chartz to {part} folder')
    # interlace filler
    no_filler_before = None
    if filler_pos == 4:
        no_filler_before = enforceRules(numbered, options["enforce-order"], title_map)
    output.extend(enumerate_pages(numbered, options, page_map=toc_maps[1], write_pages=write_pages, no_filler_before=no_filler_before, verbose=verbose))
    if filler_pos == 2: output.extend(add_filler(options))

    # Teazers
    if len(special["teazers"]):
        if verbose:
            thread_print(f'Writing teazers to {part} folder')
        output.extend(enumerate_pages(special["teazers"], options, style=1, start='a', page_map=toc_maps[2], write_pages=write_pages, verbose=verbose))
    if filler_pos == 3: output.extend(add_filler(options))

    return output

# Generates the table of contents file
def generate_toc(toc_maps, options, file, verbose=False):
    # Get page num information
    check_stop_script()
    width, height = (inch * options["page-size"]["width"], inch * options["page-size"]["height"])
    path = os.path.dirname(file)
    validate_dir(path, verbose)
    check_stop_script()
    
    # Generate toc doc and data
    toc = SimpleDocTemplate(file, pagesize=(width, height),
                            leftMargin=inch * .5, rightMargin=inch * .5,
                            topMargin=.75 * inch, bottomMargin=inch*.25)
    check_stop_script()
    styles = generate_toc_styles(options)
    data = generate_toc_data(toc_maps, options, styles)
    check_stop_script()

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
    check_stop_script()
    toc.build([table], onFirstPage=onFirstPage)
    if verbose: thread_print(f'Successfully created table of contents file at "{file}"')

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
    check_stop_script()
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

# Interlace filler pages from the "filler" list to the "pages" list, only placing filler at valid indeces
def interlace_filler(pages: List, filler: List, valid_filler_indeces):
    if len(filler) == 0: return
    filler_index = len(filler) - 1

    # add filler (in reverse order to preserve indeces)
    for index in reversed(range(0, len(valid_filler_indeces), max(1, len(valid_filler_indeces) // (len(filler) - 1)))):
        if filler_index < 0: break
        pages.insert(valid_filler_indeces[index], filler[filler_index])
        filler_index -= 1
    
    # See if there are more filler pages to add - if so, add them to the front
    if filler_index >= 0:
        print(filler_index)
        for i in range(filler_index, -1, -1):
            pages.insert(0, filler[i])

def merge_page_nums(pages: List[PageObject], options, filename='page_nums.pdf'):
    output = []
    path = os.path.join(options["folder-dir"], "tmp", filename)
    with open(path, 'rb') as f:
        page_num_pdf = PdfFileReader(f)
        for i, page in enumerate(pages):
            target: PageObject = page_num_pdf.getPage(i)
            target.mergePage(page)
            # For some reason the text doesn't appear properly if we don't write first
            thread_print("Writing extra output file because this is somehow necessary")
            tmp_out = PdfFileWriter()
            tmp_out.addPage(target)
            with open(os.path.join(options["folder-dir"], "tmp", "page_num_overlap.pdf"), 'wb') as f:
                pass#tmp_out.write(f)
            output.append(target)

    return output

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
        with open(title_map[title], "rb") as f:
            merger.append(PdfFileReader(f))
        with open(file, "rb") as f:
            merger.append(PdfFileReader(f))
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
        if verbose: thread_print(f'DEBUG: Making directory "{path}"')

# Validates that a part's files are properly formatted
def validate_part(part, options):
    path = os.path.join(options["folder-dir"], "parts", part)
    if not os.path.exists(path):
        thread_print(f'ERROR: Path to files for part "{part}" does not exist, folder will not be generated')
        return None
    
    # Validate titles
    title_map = process_files(sorted(glob.glob(f'{path}/*.pdf')))
    if len(title_map.keys()) == 0:
        thread_print(f'WARNING: No files found for part "{part}", folder will not be generated')
        return None
    validate_titles(title_map, options, resourcePath("res/options/folder_creator_options.json"), verbose=options["verbose"], part=part)

    return title_map

# Validates that a page has the proper dimensions
def validate_mediabox(mediabox: RectangleObject, options):
    width, height = (inch * options["page-size"]["width"], inch * options["page-size"]["height"])

    return (mediabox.getWidth() == width and mediabox.getHeight() == height) or (mediabox.getWidth() == height and mediabox.getHeight() == width)

# Validate and update the lists of files in the options list
def validate_titles(title_map, options, update_path=None, verbose=False, part=None):
    titles = title_map.keys()
    
    # Helper method to find case-insensitive match
    def find_match(song: str):
        song_lower = song.lower()
        for title in titles:
            if ''.join(song_lower.split()) == ''.join(title.lower().split()):
                if verbose: thread_print(f'DEBUG: Found match for song "{song}": "{title}".')
                return title

    # Go through all the file lists and make repairs if necessary
    for key in ("dollie-songs", "lettered-chartz", "exclude-songs"):
        for i, song in enumerate(options[key]):
            if not song in titles:
                if update_path:
                    match = find_match(song)
                    if match: options[key][i] = match
                    elif verbose: thread_print(f'WARNING: Song "{song}" specified in "{key}" was not found in for {part}.')
    
    for i, rule in enumerate(options["enforce-order"]):
        for j, song in enumerate(rule):
            if not song in titles:
                if update_path:
                    match = find_match(song)
                    if match: options["enforce-order"][i][j] = match
                    elif verbose: thread_print(f'WARNING: Song "{song}" specified in "enforce-order" was not found.')
    
    # Remove any songs on the exclude list
    for excluded_song in options["exclude-songs"]:
        if excluded_song in title_map:
            del title_map[excluded_song]
    
    if update_path:
        with open(update_path, 'w') as f:
            json.dump(options, f, indent=4)
