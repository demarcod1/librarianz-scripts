from .util import util

# Collects all the shortcuts in the separated directories and puts them in the archive under a new folder
def collect_shortcuts(service, ids, sep_parts, chart, chart_id, src):
    # Create "Shortcuts" folder
    shortcut_id = util.make_folder(service, "Shortcuts", chart_id)

    # Sibelius file shortcut
    for file in util.get_drive_files(service, ids[f"sib_{src}"], file_types=[".sib"], name=chart):
        util.move_file(service, file.get("id"), ids[f'sib_{src}'], shortcut_id)
    
    # Section parts file shortcut
    for _, id in sep_parts[src].items():
        for file in util.get_drive_files(service, id, file_types=".pdf", name=chart):
            util.move_file(service, file.get("id"), id, shortcut_id)

# Places the shortcuts back in their separated directories
def replace_shortcuts(service, ids, sep_parts, chart, chart_id, dst, alias_map):
    # Find "Shortcuts" folder
    res = util.get_folder_ids(service, name="Shortcuts", parent=chart_id)
    if not res or len(res) != 1:
        print(f'WARNING: Unable to find "Shortcuts" folder within "{chart}"')
        return
    shortcut_id = res[0]

    # Re-add shortcuts
    for file in util.get_drive_files(service, shortcut_id, [".pdf", ".sib"], name=chart):
        _, part, _ = util.parse_file(file.get("name"), alias_map)
        
        # If it's a sibelius file...
        if not part and file.get("name").endswith(".sib"):
            util.move_file(service, file.get("id"), shortcut_id, ids[f'sib_{dst}'])
        # If it's a pdf part...
        elif sep_parts[dst].get(part):
            util.move_file(service, file.get("id"), shortcut_id, sep_parts[dst][part])
    
    # Remove old "Shortcuts" folder
    service.files().delete(fileId=shortcut_id).execute()

def move_shortcuts(service, ids, sep_parts, chart, src, dst):
    # Move sibelius file shortcut
    for file in util.get_drive_files(service, ids[f'sib_{src}'], file_types=[".sib"], name=chart):
        util.move_file(service, file.get("id"), ids[f'sib_{src}'], ids[f'sib_{dst}'])

    # Move section part pdf shortcuts
    for part in sep_parts[src]:
        # Ensure part parity (this check should never fail)
        if not sep_parts[dst].get(part):
            continue

        for file in util.get_drive_files(service, sep_parts[src][part], [".pdf"], name=chart):
            util.move_file(service, file.get("id"), sep_parts[src][part], sep_parts[dst][part])
        
# Moves the chart to new location
def move_chart(service, ids, sep_parts, chart_to_move, alias_map):
    # Parse the destination
    chart = chart_to_move["name"]
    dest = "curr" if chart_to_move["to"] == 0 else "old" if chart_to_move["to"] == 1 else "archive"

    # Ensure we're not trying to move to the same place
    res = util.get_chart_id(service, chart, [ ids["curr"], ids["old"], ids["archive"] ])
    if res == None: return
    chart_id = res["chart_id"]
    parent_id = res["parent_id"]
    src = "curr" if parent_id == ids["curr"] else "old" if parent_id == ids["old"] else "archive" 
    if src == dest:
        print(f'WARNING: Unable to move chart "{chart}" - chart already in destination!')
        return
    
    # Move chart folder to destination
    util.move_file(service, chart_id, parent_id, ids[dest])

    # Handle shortcuts
    if (dest == "archive"):
        collect_shortcuts(service, ids, sep_parts, chart, chart_id, src)
    elif (parent_id == ids["archive"]):
        replace_shortcuts(service, ids, sep_parts, chart, chart_id, dest, alias_map)
    else:
        move_shortcuts(service, ids, sep_parts, chart, "curr" if dest == "old" else "old", dest)
    
    dirname = "Current Chartz" if dest == "curr" else "Old Chartz" if dest == "old" else "Archive/Chart Data"
    print(f'Successfully moved chart "{chart}" to "{dirname}"')

# Main method
def move_chartz():
    # Build service
    service = util.build_service()

    # Read options
    alias_map = util.make_alias_map(util.parse_options("parts.json"))
    options = util.parse_options("move_chartz_options.json")
    if options == None: return

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    library_id, curr_id, old_id = util.get_digital_library(service)
    if library_id == None: return 1

    archive_id = util.get_chart_data_archive(service, library_id)
    if archive_id == None: return 1

    ids = util.get_separated_folders(service, library_id)
    if ids == None: return 1
    
    ids.update({ "curr": curr_id, "old": old_id, "archive": archive_id })
    sep_parts = {
        age: { folder["name"]: folder["id"] for folder in util.get_drive_files(service, ids[f"sec_{age}"], files_only=False) }
            for age in ["curr", "old"]
    }

    for chart_to_move in options["chartz"]:
        print(f'Moving chart {chart_to_move["name"]}...')
        move_chart(service, ids, sep_parts, chart_to_move, alias_map)
    
    return 0