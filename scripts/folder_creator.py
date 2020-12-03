from scripts.util.thread_events import check_stop_script, thread_print
import threading, concurrent.futures
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
    thread_print(f'Writing {part} folder...')
    title_map = pdf_tools.validate_part(part, options)
    if not title_map: return 1
    check_stop_script()

    # Write pages
    output = PdfFileWriter()
    toc_maps = [ {}, {}, {} ]
    for page in pdf_tools.generate_parts_pages(title_map, toc_maps, options, part, write_pages=True, verbose=options['verbose']):
        output.addPage(page)
    
    # Add table of contents (toc)
    if options['verbose']: thread_print(f'Generating {part} Table of Contents')
    pdf_tools.generate_toc(toc_maps, options, toc_path)
    output.insertPage(pdf_tools.to_pages(toc_path)[0], 0)

    # Write file
    check_stop_script()
    file_path = os.path.join(options["folder-dir"], "Output")
    pdf_tools.validate_dir(file_path, options["verbose"])
    with open(os.path.join(file_path,  f'{options["folder-name"]} - {part}.pdf'), 'wb') as f:
        output.write(f)
    thread_print(f'Successfully wrote {part} folder to "{file_path}"')

    # Cleanup temp files
    if os.path.isfile(toc_path):
        os.remove(toc_path)
    
    return 0

# Main  method
def folder_creator(max_workers = 10):
    options = parse_options("folder_creator_options.json")
    if options == None: return 1

    with concurrent.futures.ThreadPoolExecutor(max_workers) as threadPool:
        futures = {threadPool.submit(create_part_folder, part, options): part for part in options['folder-parts']}
        for future in concurrent.futures.as_completed(futures):
            pass
        

 
    thread_print("Finished generating folders")
    
    return 0