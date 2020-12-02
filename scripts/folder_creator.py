from queue import Queue
import threading, queue
from typing import List
from .util.util import parse_options
from .util import pdf_tools
from PyPDF2 import PdfFileWriter
import os

# Folder creator per part fn (thread target)
def create_part_folder(part, options):
    # Table of contents + page number path
    toc_path = os.path.join(options["folder-dir"], "tmp", f"toc-{part}.pdf")

    # Validate part files
    print(f'Writing {part} folder...\n')
    title_map = pdf_tools.validate_part(part, options)
    if not title_map: return 1

    # Write pages
    output = PdfFileWriter()
    toc_maps = [ {}, {}, {} ]
    for page in pdf_tools.generate_parts_pages(title_map, toc_maps, options, write_pages=True, verbose=options['verbose']):
        output.addPage(page)
    
    # Add table of contents (toc)
    if options['verbose']: print(f'Generating {part} Table of Contents')
    pdf_tools.generate_toc(toc_maps, options, toc_path)
    output.insertPage(pdf_tools.to_pages(toc_path)[0], 0)

    # Write file
    file_path = os.path.join(options["folder-dir"], "Output")
    pdf_tools.validate_dir(file_path, options["verbose"])
    with open(os.path.join(file_path,  f'{options["folder-name"]} - {part}.pdf'), 'wb') as f:
        output.write(f)
    print(f'Successfully wrote {part} folder to "{file_path}"')

    # Cleanup temp files
    if os.path.isfile(toc_path):
        os.remove(toc_path)
    
    return 0

# Main  method
def folder_creator():
    queue = Queue()

    options = parse_options("folder_creator_options.json")
    if options == None: return 1

    threads: List[threading.Thread] = []
    for part in options["folder-parts"]:
        new_thread = threading.Thread(target=create_part_folder, daemon=True, args=(part, options))
        threads.append(new_thread)
        new_thread.start()
    
    for thread in threads:
        thread.join()
 
    print("Finished generating folders")
    
    return 0