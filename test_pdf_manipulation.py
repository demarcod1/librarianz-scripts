from util.util import parse_options
import util.pdf_tools as pdf_tools
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import glob, os


def main():
    options = parse_options("folder_creator_options.json")
    path = os.path.join(options["parts-dir"], "Bonz")
    output = PdfFileWriter()

    i = 1
    for file in sorted(glob.glob(f'{path}/*.pdf')):
        try:
            input_page = PdfFileReader(open(file, 'rb')).getPage(0)
            output.addPage(pdf_tools.add_page_num(input_page, f'{i}', options))
            i += 1
        except:
            print(f'Error when parsing "{file}"')
    
    with open('../tmp/New PDF.pdf', 'wb') as f:
        output.write(f)


if __name__ == '__main__':
    main()