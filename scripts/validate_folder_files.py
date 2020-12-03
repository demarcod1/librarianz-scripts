import os
from scripts.util.util import parse_options
import scripts.util.pdf_tools as pdf_tools
from scripts.util.thread_events import check_stop_script

# Creates a mock table of contents to ensure everything works as expected
def validate_toc(part, title_map, options):
    toc_maps = [ {}, {}, {} ]
    file = os.path.join(options["folder-dir"], "Output", f'Table of Contents - {part}.pdf')

    # Generate the table of contents
    pdf_tools.generate_parts_pages(title_map, toc_maps, options, write_pages=False)
    pdf_tools.generate_toc(toc_maps, options, file, verbose=True)

# Main method
def validate_folder_files():
    options = parse_options("folder_creator_options.json")
    if options == None: return 1

    for part in options["folder-parts"]:
        check_stop_script()

        # Validate part files
        title_map = pdf_tools.validate_part(part, options)
        if not title_map: continue

        # Generate sample table of contents
        if options["toc"]["generate-on-validation"]:
            validate_toc(part, title_map, options)
    
    print("Finished validating folders and parts")
    return 0