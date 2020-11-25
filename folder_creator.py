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
        toc_path = os.path.join(options["folder-dir"], "tmp", "toc.pdf")
        pdf_tools.generate_toc(toc_maps, options, toc_path)
        output.insertPage(pdf_tools.to_pages(toc_path)[0], 0)
        os.remove(toc_path)

        # Write file
        file_path = os.path.join(options["folder-dir"], "Output")
        pdf_tools.validate_dir(file_path, options["verbose"])
        with open(os.path.join(file_path,  f'{options["folder-name"]} - {part}.pdf'), 'wb') as f:
            output.write(f)
        print(f'Finished writing {part} folder to "{file_path}"')


if __name__ == '__main__':
    main()