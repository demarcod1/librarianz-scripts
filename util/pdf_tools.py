import os
import util.util as util
from PyPDF2 import PdfFileWriter, PdfFileReader
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
