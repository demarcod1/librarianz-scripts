from .util import util
from .util import lib_management

# Main method
def upload_files():
    # A quick print statement to let the user know what script they're running
    print("Starting Upload Files script...")

    # Build service
    service = util.build_service()

    # Read options
    alias_map = util.make_alias_map(util.parse_options("parts.json"))
    options = util.parse_options("upload_options.json")
    if options == None: return 1

    # Get list of files that need to be uploaded
    files = util.get_dir_files(options["resources-directory"], options["supported-file-types"])

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    library_id, curr_id, old_id = util.get_digital_library(service)
    if library_id == None: return 1
    
    separated_ids = util.get_separated_folders(service, library_id)
    if separated_ids == None: return 1

    # Cache will store folder + parts folder ids and a list of files
    cache = {}

    # 0 = update only, 1 = new files only, 2 = update and add new files
    mode = options["mode"]

    # Create new folders (if in proper mode)
    if mode != 0:
        for chart_info in options["new-chartz"]:
            is_curr = chart_info["to"] == 0
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
        elif updated == False:
            print(f'ERROR: Unable to update "{file}"')
    
    return 0
