from util.util import parse_options
import util.pdf_tools as pdf_tools
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import glob, os


def main():
    options = parse_options("folder_creator_options.json")
    path = os.path.join(options["parts-dir"], "Trumpz")
    output = PdfFileWriter()
    title_map = pdf_tools.process_files(sorted(glob.glob(f'{path}/*.pdf')))
    lettered, numbered, fingering_chart = pdf_tools.categorize_parts(title_map, options)

    for page in pdf_tools.enumerate_pages(lettered, options, style=1):
        output.addPage(page)
    
    for page in pdf_tools.enumerate_pages(numbered, options):
        output.addPage(page)
    
    with open('../test_folder/tmp/Duplicate titles test.pdf', 'wb') as f:
        output.write(f)


if __name__ == '__main__':
    main()