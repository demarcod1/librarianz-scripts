import util.util as util
import util.pdf_tools as pdf_tools

def main():
    service = util.build_service()
    options = util.parse_options("folder_creator_options.json")

    # Get a random chart's folder
    print("Verifying DigitalLibrary format...")
    library_id, _, _ = util.get_digital_library(service)
    curr_parts_id = util.get_separated_folders(service, library_id)["sec_curr"]

    pdf_tools.download_part_files(service, curr_parts_id, "Bonz", options["parts-dir"], True)

if __name__ == '__main__':
    main()