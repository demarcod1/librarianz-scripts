from scripts.util.thread_events import check_stop_script
from scripts.util import util

# List of acceptable resources
RESOURCES = [".mid", ".mp3", ".mp4", ".mov", ".wav", ".wmv", ".m4a"]

# Verify redvest location and create new class folder
def verify_redvest(service, redvest_options):
    # Ensure redvest folder exists
    check_stop_script()
    parent_name = redvest_options['parent-name']
    res = util.get_folder_ids(service, name=parent_name)
    if res == None:
        print(f'ERROR: "{parent_name}" folder not found in Red Vest directory, please check Google Drive')
        return None, None
    redvest_id = res[0]

    folder_name = redvest_options["folder-name"]

    # See if target folder already exists
    if util.get_folder_ids(service, name=folder_name, parent=redvest_id) != None:
        print(f'ERROR: Folder \"{folder_name}\" already exists!')
        print("(You may need to remove the folder from the Trash in the Librarianz Drive)")
        return None, None

    # Create new class folder
    new_folder_id = util.make_folder(service, folder_name, redvest_id)

    # Create resources folder
    new_resources_id = util.make_folder(service, "Resources", new_folder_id)

    return new_folder_id, new_resources_id

def make_section_folders(service, new_folder_id, parts):
    output = {}
    instrument_folder_id = util.make_folder(service, "Parts by Instrument", new_folder_id)
    audio_folder_id = util.make_folder(service, "Audio by Instrument", new_folder_id)

    for id, abbr in ((instrument_folder_id, 'sec'), (audio_folder_id, 'aud')):
        output[abbr] = {}
        for part in parts:
            output[abbr][part] = util.make_folder(service, part, id)
    return output        

def add_parts_shortcut(service, chart, chart_id, new_folder_id, section_ids=None, alias_map=None):
    # Search for parts folder
    parts_id, audio_id = util.get_parts_and_audio_folders(service, chart, chart_id)
    if (parts_id == None): return
    
    # Create shortcut in Redvest folder
    util.make_shortcut(service, chart, parts_id, new_folder_id)

    # Add individual parts
    if (not section_ids or not alias_map): return
    add_individual_parts(service, parts_id, audio_id, section_ids, alias_map)

def add_individual_parts(service, parts_id, audio_id, section_ids, alias_map):
    # Get and process parts
    for id, abbr in ((parts_id, 'sec'), (audio_id, 'aud')):
        if id == None: continue
        for item in util.get_drive_files(service, id):
            check_stop_script()
            _, part, _ = util.parse_file(item.get('name'), alias_map)

            # Part mapping doesn't exist
            if (part == util.NO_PART or not part):
                print(f'WARNING: Cannot add "{item.get("name")}" - part not found')
                continue
            
            # Make shortcut
            util.make_shortcut(service, item.get('name'), item.get('id'), section_ids[abbr][part])

def add_resources(service, chart, chart_id, new_resources_id):
    # Search chart folder for audio/video resources
    items = util.get_drive_files(service, chart_id, RESOURCES)
    
    # Add shortcuts to these resources
    for item in items:
        util.make_shortcut(service, item.get('name'), item.get('id'), new_resources_id)
    
    if len(items) == 0:
        print(f'WARNING: Resource files not found for "{chart}"')

def write_song(service, chart, chart_id, new_folder_id, new_resources_id, section_ids=None, alias_map=None):
    check_stop_script()
    print(f"Writing chart \"{chart}\"...")

    # add shortcut to parts folder
    check_stop_script()
    add_parts_shortcut(service, chart, chart_id, new_folder_id, section_ids, alias_map)

    # add audio/video content to 'Resources' folder
    check_stop_script()
    add_resources(service, chart, chart_id, new_resources_id)

def verify_chart_name(service, chart, parent_ids):
    check_stop_script()
    chart_id = util.get_chart_id(service, chart, parent_ids).get("chart_id")
    return chart_id

# Main method
def redvest_creator():
    # Build service
    service = util.build_service()

    # Read folder locations
    redvest_options = util.parse_options("redvest_options.json")
    if redvest_options == None: return 1

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    lib_ids = util.get_digital_library(service)
    current_chartz_id = lib_ids.get("current_id")
    future_chartz_id = lib_ids.get("future_id")
    if current_chartz_id == None or future_chartz_id == None: return 1

    # Verify (and collect) all chart ids
    print("Validating Chartz...")
    chart_ids = [verify_chart_name(service, chart, [current_chartz_id, future_chartz_id]) for chart in redvest_options["chartz"]]
    if None in chart_ids:
        print('Try double-check your spelling, chart names are case-sensitive')
        print('ERROR: Redvest folder will not be created')
        return 1

    print("Verifying Redvest folder...")
    new_folder_id, new_resources_id = verify_redvest(service, redvest_options)
    if new_folder_id == None or new_resources_id == None: return 1

    # Only make individual section folders if field set to true
    alias_map = None
    section_ids = None
    check_stop_script()
    if redvest_options["individual-sections"]:
        # Read parts
        parts_dict = util.parse_options("parts.json")['parts']
        if parts_dict == None: return 1
        
        # Make individual section folders
        print("Making individual section folders...")
        section_ids = make_section_folders(service, new_folder_id, parts_dict.keys())

        # Invert parts_dict to create map of alias's -> folder
        alias_map = util.make_alias_map(parts_dict)


    # Write each chart to the new redvest folder
    for index, chart in enumerate(redvest_options["chartz"]):
        write_song(service, chart, chart_ids[index], new_folder_id, new_resources_id, section_ids, alias_map)
    
    print(f'Successfully created new folder "{redvest_options["folder-name"]}"!')
    return 0
