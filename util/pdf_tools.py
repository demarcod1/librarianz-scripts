import os
from typing import Dict
import util.util as util
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Adds the page number (or any arbitrary text) to the chart pdf file
def add_page_num(page, text: str, options):
    # Get page num information
    width, height = (72 * options["page-size"]["width"], 72 * options["page-size"]["height"])
    font, size = (options["page-num-font"]["name"], options["page-num-font"]["size"])
    path = os.path.join(options["tmp-dir"], "page_num.pdf")

    # Draw text on canvas
    page_num = canvas.Canvas(path, pagesize=(width, height))
    page_num.setFont(font, size)
    page_num.drawCentredString(1.5 * inch, height - (.02 * size * inch), text)
    page_num.showPage()
    page_num.save()

    # Add page number to existing page
    page_num = PdfFileReader(open(path, 'rb')).getPage(0)
    page.mergePage(page_num)
    return page

# Splits the raw list of parts files into lists of Lettered, Numbered, fingering chart
def categorize_parts(title_map, options):
    lettered, numbered, fingering_chart = [], [], []
    for title in title_map:
        # parse filename
        file = title_map[title]

        # check to see if it's a fingering chart
        if options["fingering-chart"]["include"] and options["fingering-chart"]["prefix"] in title:
            fingering_chart.append(file)
        
        # check to see if it's a lettered chart
        elif title in options["lettered-chartz"]:
            lettered.append(file)

        # by default, it's a numbered chart
        else:
            numbered.append(file)

    for list in (lettered, numbered):
        enforceRules(list, options["enforce-order"], title_map)

    return lettered, numbered, fingering_chart

# Downloads all the files from a Separated Section Parts folder
def download_part_files(service, curr_parts_id, part, dir, verbose=False):
    # Validate target directory
    path = os.path.join(dir, part)
    if not os.path.exists(path):
        os.makedirs(path)
        if verbose: print(f'DEBUG: Making directory "{path}"')
    
    # Retrieve files
    folders = util.get_drive_files(service, curr_parts_id, files_only=False, name=part)
    if not folders or len(folders) != 1:
        print(f'WARNING: Unable to find folder "{part}"')
    files = util.get_drive_files(service, folders[0].get("id"), file_types=[".pdf"], is_shortcut=True)
    if not files or len(files) == 0:
        print(f'WARNING: Could not find any part files for "{part}"')
    
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
# Style: 0 = numbers, 1 = Letters
def enumerate_pages(files, options, style=0, start=None, page_map=None):
    pages = []
    if start == None:
        start = 1 if style == 0 else 'A'
    counter = start

    for file in files:
        try:
            # Read input file
            input = PdfFileReader(open(file, 'rb'))
            num_pages = input.getNumPages()
            page_num = f'{counter}'

            # Save page num assignment to map
            if page_map: page_map[counter] = file

            # Add all the pages to the list
            for i in range(num_pages):
                input_page = input.getPage(i)
                if num_pages > 1: page_num = f'{counter}.{i + 1}'
                pages.append(add_page_num(input_page, page_num, options))
        except:
            print(f'Error when parsing "{file}"')
        
        # Increment Counter
        counter = (counter + 1) if style == 0 else (chr(ord(counter) + 1))

    return pages

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
