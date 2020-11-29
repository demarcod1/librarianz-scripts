from .util.util import parse_options
from .util import pdf_tools
from PyPDF2 import PdfFileWriter
import os

# Main  method
def folder_creator():
    options = parse_options("folder_creator_options.json")
    if options == None: return 1

    # Table of contents + page number path
    toc_path = os.path.join(options["folder-dir"], "tmp", "toc.pdf")
    page_num_path = os.path.join(options["folder-dir"], "tmp", "page_num.pdf")

    for part in options["folder-parts"]:
        # Validate part files
        print(f'Writing {part} folder...')
        title_map = pdf_tools.validate_part(part, options)
        if not title_map: continue

        # Write pages
        output = PdfFileWriter()
        toc_maps = [ {}, {}, {} ]
        for page in pdf_tools.generate_parts_pages(title_map, toc_maps, options, write_pages=True, verbose=options['verbose']):
            output.addPage(page)
        
        # Add table of contents (toc)
        pdf_tools.generate_toc(toc_maps, options, toc_path)
        output.insertPage(pdf_tools.to_pages(toc_path)[0], 0)

        # Write file
        file_path = os.path.join(options["folder-dir"], "Output")
        pdf_tools.validate_dir(file_path, options["verbose"])
        with open(os.path.join(file_path,  f'{options["folder-name"]} - {part}.pdf'), 'wb') as f:
            output.write(f)
        print(f'Successfully wrote {part} folder to "{file_path}"')

    # Cleanup temp files
    for path in (toc_path, page_num_path):
        if os.path.isfile(path):
            os.remove(path)
    
    print("Finished generating folders")
    
    return 0