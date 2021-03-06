from scripts.util.thread_events import check_stop_script
from scripts.util import util

# Collects all the shortcuts in the separated directories and puts them in the archive under a new folder
def collect_shortcuts(service, ids, sep_parts, sep_audio, chart, chart_id, src):
    # Create "Shortcuts" folder
    shortcut_id = util.make_folder(service, "Shortcuts", chart_id)

    # Sibelius file shortcut
    for file in util.get_drive_files(service, ids[f"sib_{src}"], file_types=[".sib"], name=chart):
        util.move_file(service, file.get("id"), ids[f'sib_{src}'], shortcut_id)
    
    # Section parts and audio file shortcuts
    for sep_data in (sep_parts, sep_audio):
        for _, id in sep_data[src].items():
            for file in util.get_drive_files(service, id, name=chart):
                util.move_file(service, file.get("id"), id, shortcut_id)

# Places the shortcuts back in their separated directories
def replace_shortcuts(service, ids, sep_parts, sep_audio, chart, chart_id, dst, alias_map):
    # Find "Shortcuts" folder
    res = util.get_folder_ids(service, name="Shortcuts", parent=chart_id)
    if res == None:
        print(f'WARNING: Unable to find "Shortcuts" folder within "{chart}"')
        return
    shortcut_id = res[0]

    # Re-add shortcuts
    for file in util.get_drive_files(service, shortcut_id, name=chart):
        _, part, mimeType = util.parse_file(file.get("name"), alias_map)
        
        # If it's a sibelius file...
        if not part and file.get("name").endswith(".sib"):
            util.move_file(service, file.get("id"), shortcut_id, ids[f'sib_{dst}'])
        # If it's a pdf part...
        elif sep_parts[dst].get(part) and mimeType == 'application/pdf' or file.get("name").endswith(".pdf"):
            util.move_file(service, file.get("id"), shortcut_id, sep_parts[dst][part])
        # If it's an audio part...
        elif sep_audio[dst].get(part) and mimeType.startswith('audio'):
            util.move_file(service, file.get("id"), shortcut_id, sep_audio[dst][part])
    
    # Remove old "Shortcuts" folder
    service.files().delete(fileId=shortcut_id).execute()

def move_shortcuts(service, ids, sep_parts, sep_audio, chart, src, dst):
    # Move sibelius file shortcut
    for file in util.get_drive_files(service, ids[f'sib_{src}'], file_types=[".sib"], name=chart):
        util.move_file(service, file.get("id"), ids[f'sib_{src}'], ids[f'sib_{dst}'])

    # Move section part pdf shortcuts
    for sep_dir in (sep_parts, sep_audio):
        for part in sep_dir[src]:
            # Ensure part parity (this check should never fail)
            if not sep_dir[dst].get(part):
                continue

            for file in util.get_drive_files(service, sep_dir[src][part], name=chart):
                util.move_file(service, file.get("id"), sep_dir[src][part], sep_dir[dst][part])
        
# Moves the chart to new location
def move_chart(service, ids, sep_parts, sep_audio, chart_to_move, alias_map):
    # Parse the destination
    chart = chart_to_move["name"]
    raw_dest = chart_to_move["to"]
    dest = "curr" if raw_dest == 0 else "old" if raw_dest == 1 else "future" if raw_dest == 2 else "archive"

    # Ensure we're not trying to move to the same place
    check_stop_script()
    res = util.get_chart_id(service, chart, [ ids["curr"], ids["old"], ids["future"], ids["archive"] ])
    if res["chart_id"] == None: return
    chart_id = res["chart_id"]
    parent_id = res["parent_id"]
    src = "curr" if parent_id == ids["curr"] else "old" if parent_id == ids["old"] else "future" if parent_id == ids["future"] else "archive" 
    if src == dest:
        print(f'ERROR: Unable to move chart "{chart}" - chart already in destination!')
        return
    
    # Move chart folder to destination
    check_stop_script()
    util.move_file(service, chart_id, parent_id, ids[dest])

    # Handle shortcuts
    if (dest == "archive"):
        collect_shortcuts(service, ids, sep_parts, sep_audio, chart, chart_id, src)
    elif (src == "archive"):
        replace_shortcuts(service, ids, sep_parts, sep_audio, chart, chart_id, dest, alias_map)
    else:
        move_shortcuts(service, ids, sep_parts, sep_audio, chart, src, dest)
    
    dirname = "Current Chartz" if dest == "curr" else "Old Chartz" if dest == "old" else "Future Chartz" if dest == "future" else "Archive/Chart Data"
    print(f'Successfully moved chart "{chart}" to "{dirname}"')

# Main method
def move_chartz():
    # Build service
    service = util.build_service()

    # Read options
    alias_map = util.make_alias_map(util.parse_options("parts.json")['parts'])
    options = util.parse_options("move_chartz_options.json")
    if options == None: return

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    lib_ids = util.get_digital_library(service)
    library_id = lib_ids.get("library_id")
    curr_id = lib_ids.get("current_id")
    old_id = lib_ids.get("past_id")
    future_id = lib_ids.get("future_id")
    if library_id == None: return 1

    archive_id = util.get_chart_data_archive(service, library_id)
    if archive_id == None: return 1

    ids = util.get_separated_folders(service, library_id)
    if ids == None: return 1
    
    ids.update({ "curr": curr_id, "old": old_id, "future": future_id, "archive": archive_id })
    sep_parts = {
        age: { folder["name"]: folder["id"] for folder in util.get_drive_files(service, ids[f"sec_{age}"], files_only=False) }
            for age in ["curr", "old", "future"]
    }
    sep_audio = {
        age: { folder["name"]: folder["id"] for folder in util.get_drive_files(service, ids[f"aud_{age}"], files_only=False) }
            for age in ["curr", "old", "future"]
    }

    for chart_to_move in options["chartz"]:
        print(f'Moving chart {chart_to_move["name"]}...')
        move_chart(service, ids, sep_parts, sep_audio, chart_to_move, alias_map)

    print("Finished moving chartz")
    return 0