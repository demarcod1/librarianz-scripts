from util.util import parse_options
import util.pdf_tools as pdf_tools
from PyPDF2 import PdfFileWriter
import os


def main():
    options = parse_options("folder_creator_options.json")

    for part in options["folder-parts"]:
        # Validate part files
        print(f'Writing {part} folder...')
        title_map = pdf_tools.validate_part(part, options)
        if not title_map: continue

        # Write pages
        output = PdfFileWriter()
        toc_maps = [ {}, {}, {} ]
        for page in pdf_tools.generate_parts_pages(title_map, toc_maps, options, write_pages=True):
            output.addPage(page)
        
        # Add table of contents (toc)
        pdf_tools.generate_toc(toc_maps, options, os.path.join(options["folder-dir"], "tmp", "toc.pdf"))
        output.insertPage(pdf_tools.to_pages(os.path.join(options["folder-dir"], "tmp", "toc.pdf"))[0], 0)

        # Write file
        file_path = os.path.join(options["folder-dir"], "Output")
        if not os.path.exists(file_path):
            if options["verbose"]: print(f'DEBUG: Creating directory "{file_path}"')
            os.makedirs(file_path)
        with open(os.path.join(file_path,  f'{options["folder-name"]} - {part}.pdf'), 'wb') as f:
            output.write(f)
        print(f'Finished writing {part} folder to "{file_path}"')


if __name__ == '__main__':
    main()