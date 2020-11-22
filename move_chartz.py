import util.util as util

def main():
    # Build service
    service = util.build_service()

    # Read options
    alias_map = util.make_alias_map(util.parse_options("parts.json"))
    options = util.parse_options("upload_options.json")

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    library_id, curr_id, old_id = util.get_digital_library(service)
    separated_ids = util.get_separated_folders(service, library_id)

if __name__ == '__main__':
    main()