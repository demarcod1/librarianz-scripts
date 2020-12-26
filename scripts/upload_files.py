from scripts.util.thread_events import check_stop_script
from scripts.util import util
from scripts.util import lib_management

# Main method
def upload_files():
    # Build service
    service = util.build_service()

    # Read options
    alias_map = util.make_alias_map(util.parse_options("parts.json")['parts'])
    options = util.parse_options("upload_options.json")
    if options == None: return 1
    check_stop_script()

    # Get list of files that need to be uploaded
    files = util.get_dir_files(options["resources-directory"], options["supported-file-types"])
    check_stop_script()

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    lib_ids = util.get_digital_library(service)
    library_id = lib_ids.get("library_id")
    if library_id == None: return 1
    check_stop_script()
    
    separated_ids = util.get_separated_folders(service, library_id)
    if separated_ids == None: return 1
    check_stop_script()

    # Cache will store folder + parts folder ids and a list of files
    cache = {}

    # 0 = update only, 1 = new files only, 2 = update and add new files
    mode = options["mode"]

    # Create new folders (if in proper mode)
    if mode != 0:
        for chart_info in options["new-chartz"]:
            check_stop_script()
            chart_dest = chart_info["to"]
            new_chart_dest_key = "current_id" if chart_dest == 0 else "past_id" if chart_dest == 1 else "future_id" 
            chart_id, parts_id = lib_management.create_chart_structure(service, lib_ids.get(new_chart_dest_key), chart_info["name"])
            if chart_id:
                cache[chart_info["name"]] = { "chart_id": chart_id, "parts_id": parts_id, "loc": chart_info["to"], "files": [] }
    
    # Operate on files
    for file in files:
        # Check to see if we should exit
        check_stop_script()

        # Populate cache
        lib_management.populate_cache(service, lib_ids.get("current_id"), lib_ids.get("past_id"), lib_ids.get("future_id"), util.parse_file(file, alias_map)[0], cache, options)
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
    
    print("Finished uploading files")
    return 0
