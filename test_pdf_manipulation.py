from util.pdf_tools import to_pages
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
    title_map = pdf_tools.process_files(sorted(glob.glob(f'{path}/*.pdf')))
    toc_maps = [ {}, {}, {} ]
    lettered, numbered, special = pdf_tools.categorize_parts(title_map, options)

    if len(special["fingering_chart"]):
        for page in pdf_tools.to_pages(special["fingering_chart"][0]):
            output.addPage(page)

    for page in pdf_tools.enumerate_pages(lettered, options, style=1, page_map=toc_maps[0]):
        output.addPage(page)
    
    for page in pdf_tools.enumerate_pages(numbered, options, page_map=toc_maps[1]):
        output.addPage(page)
    
    if len(special["teazers"]):
        for page in pdf_tools.enumerate_pages(special["teazers"], options, style=1, start='a', page_map=toc_maps[2]):
            output.addPage(page)
    
    pdf_tools.generate_toc(toc_maps, options)
    output.insertPage(pdf_tools.to_pages(os.path.join(options["tmp-dir"], "toc.pdf"))[0], 0)

    with open('../test_folder/tmp/TOC Test.pdf', 'wb') as f:
        output.write(f)


if __name__ == '__main__':
    main()