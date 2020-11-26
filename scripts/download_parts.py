from .util import util
from .util import pdf_tools
import os

# Main method
def download_parts():
    service = util.build_service()
    options = util.parse_options("folder_creator_options.json")

    # Ensure that there are parts to download
    if len(options["download-parts"]) == 0:
        print(f'ERROR: No parts specified.')
        return

    # Get the current parts id
    print("Verifying DigitalLibrary format...")
    library_id, _, _ = util.get_digital_library(service)
    curr_parts_id = util.get_separated_folders(service, library_id)["sec_curr"]

    for part in options["download-parts"]:
        print(f'Downloading files for part "{part}"')
        pdf_tools.download_part_files(service, curr_parts_id, part, os.path.join(options["folder-dir"], "parts"), options["verbose"])