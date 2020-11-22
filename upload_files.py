import util.util as util
import util.lib_management as lib_management

def main():
    # Build service
    service = util.build_service()

    # Read options
    alias_map = util.make_alias_map(util.parse_options("parts.json"))
    options = util.parse_options("upload_options.json")

    # Get list of files that need to be uploaded
    files = util.get_dir_files(options["resources-directory"], options["supported-file-types"])

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    library_id, curr_id, old_id = util.get_digital_library(service)
    sep_sib_ids = util.get_separated_folders(service, library_id, "Separated Sibelius Files")
    sep_sec_ids = util.get_separated_folders(service, library_id, "Separated Section Parts")
    separated_ids = {
        "sib_curr": sep_sib_ids[0],
        "sib_old": sep_sib_ids[1],
        "sec_curr": sep_sec_ids[0],
        "sec_old": sep_sec_ids[1]
    }

    # Cache will store folder + parts folder ids and a list of files
    cache = {}

    # 0 = update only, 1 = new files only, 2 = update and add new files
    mode = options["mode"]

    # Create new folders (if in proper mode)
    if mode != 0:
        for chart_info in options["new-chartz"]:
            is_curr = chart_info["is-current"]
            chart_id, parts_id = lib_management.create_chart_structure(service, curr_id if is_curr else old_id, chart_info["name"])
            if chart_id:
                cache[chart_info["name"]] = { "chart_id": chart_id, "parts_id": parts_id, "is_current": is_curr, "files": [] }
    
    # Operate on files
    for file in files:
        # Populate cache
        lib_management.populate_cache(service, curr_id, old_id, util.parse_file(file, alias_map)[0], cache, options)
        updated = None
        added = None

        # Update file
        if mode != 1:
            updated = lib_management.update_file(service, file, alias_map, cache, options)
        
        # Add file
        if mode != 0 and not updated:
            added = lib_management.add_file(service, file, separated_ids, alias_map, cache, options)

        # print output
        if updated == True:
            print(f'Successfully updated "{file}"')
        elif added == True:
            print(f'Successfully added "{file}"')

if __name__ == '__main__':
    main()
    