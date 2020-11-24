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

    # chart_id = util.get_chart_id(service, "You Can Call Me Al", [curr_id])["chart_id"]
    # parts_id = util.get_parts_folder(service, "You Can Call Me Al", chart_id)
    # files = util.get_drive_files(service, parts_id, [".pdf"])

    # for file in files:
    #     util.download_file(service, file["id"], "../tmp/", file["name"], True)

if __name__ == '__main__':
    main()