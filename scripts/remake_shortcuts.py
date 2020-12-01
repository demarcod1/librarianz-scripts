import scripts.util.util as util
import scripts.util.remake_utils as rm

# Retrieves a list of all shortcuts in the Digital Li

# Main method
def remake_shortcuts():
    # Build drive
    service = util.build_service()

    # Read options
    parts = util.parse_options("parts.json")
    parts_dict = parts['parts']
    alias_map = util.make_alias_map(parts_dict)

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    library_id, curr_id, old_id = util.get_digital_library(service)
    if library_id == None: return 1

    live_id = rm.get_lsjumb_digital_chartz_id(service, library_id)
    prev_live_curr_id, prev_live_old_id = rm.get_curr_old_live_ids(service, live_id)

    sep_ids = util.get_separated_folders(service, library_id)
    if sep_ids == None: return 1

    print("Retrieving chart data...")
    all_chartz = rm.get_all_chart_folders(service, curr_id, old_id)

    print("Creating Separated Section Parts and Sibelius Files folders...")
    new_folders = rm.new_sep_structure(service, sep_ids['sec'], sep_ids['sib'], parts_dict)

    # Write shortcuts
    for age in all_chartz:
        for chartname, id in all_chartz[age].items():
            print(f'Writing Shortcuts for "{chartname}"')
            rm.write_shortcuts(service, chartname, id, age, new_folders, alias_map)

    # Add non-excluded files to the Live library
    print("Adding shortcuts to Live Digital Library...")
    new_live_curr_id, new_live_old_id = rm.add_live_part_folders(service, live_id)
    if not new_live_curr_id or not new_live_old_id: return 1
    
    for parent, age in [(new_live_curr_id, 'curr'), (new_live_old_id, 'old')]:
        rm.add_live_part_shortcuts(service, parent, age, new_folders, parts['exclude'])
    
    # Deleting old shortcut container folders
    print("Removing old Separated Parts/Sibelius folders...")
    rm.delete_files(service, [
        prev_live_curr_id,
        prev_live_old_id,
        sep_ids['sec_old'],
        sep_ids['sec_curr'],
        sep_ids['sib_old'],
        sep_ids['sib_curr']
        ])
    
    print("Successfully remade shortcuts - changes are live!")
    print('Make sure that the "Current Chartz" and "Old Chartz" folders within the "Separated Sibelius Files" directory are shared with anyone who has the link')
    return 0

