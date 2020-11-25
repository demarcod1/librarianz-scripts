import os
from util.util import parse_options
import util.pdf_tools as pdf_tools

# Creates a mock table of contents to ensure everything works as expected
def validate_toc(part, title_map, options):
    verbose = options["verbose"]
    toc_maps = [ {}, {}, {} ]
    file = os.path.join(options["folder-dir"], "Output", f'{part} - Table of Contents.pdf')

    # Generate the table of contents
    pdf_tools.generate_parts_pages(title_map, toc_maps, options, write_pages=False)
    pdf_tools.generate_toc(toc_maps, options, file, verbose)

def main():
    options = parse_options("folder_creator_options.json")

    for part in options["folder-parts"]:        
        # Validate part files
        title_map = pdf_tools.validate_part(part, options)
        if not title_map: continue

        # Generate sample table of contents
        if options["toc"]["generate-on-validation"]:
            validate_toc(part, title_map, options)  


if __name__ == '__main__':
    main()