from .util import util
import sys

# List of acceptable resources
RESOURCES = [".mid", ".mp3", ".mp4", ".mov", ".wav", ".wmv"]

# Verify redvest location and create new class folder
def verify_redvest(service, redvest_options):
    # Ensure redvest folder exists
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
    for part in parts:
        output[part] = util.make_folder(service, part, instrument_folder_id)
    return output        

def add_parts_shortcut(service, chart, chart_id, new_folder_id, section_ids=None, alias_map=None):
    # Search for parts folder
    parts_id = util.get_parts_folder(service, chart, chart_id)
    if (parts_id == None): return
    
    # Create shortcut in Redvest folder
    util.make_shortcut(service, chart, parts_id, new_folder_id)

    # Add individual parts
    if (not section_ids or not alias_map): return
    add_individual_parts(service, parts_id, section_ids, alias_map)

def add_individual_parts(service, parts_id, section_ids, alias_map):
    # Get and process parts
    for item in util.get_drive_files(service, parts_id, [".pdf"]):
        alias = item.get('name').split('-')[-1].strip()[:-4]
        part = alias_map.get(alias)

        # Part mapping doesn't exist
        if (not part):
            print(f'WARNING: Cannot add "{item.get("name")}" - part not found')
            continue
        
        # Make shortcut
        util.make_shortcut(service, item.get('name'), item.get('id'), section_ids[part])

def add_resources(service, chart, chart_id, new_resources_id):
    # Search chart folder for audio/video resources
    items = util.get_drive_files(service, chart_id, RESOURCES)
    
    # Add shortcuts to these resources
    for item in items:
        util.make_shortcut(service, item.get('name'), item.get('id'), new_resources_id)
    
    if len(items) == 0:
        print(f'WARNING: Resource files not found for "{chart}"')

def write_song(service, chart, current_chartz_id, new_folder_id, new_resources_id, section_ids=None, alias_map=None):
    print(f"Writing chart \"{chart}\"...")

    chart_id = util.get_chart_id(service, chart, [current_chartz_id]).get("chart_id")
    if (chart_id == None): return

    # add shortcut to parts folder
    add_parts_shortcut(service, chart, chart_id, new_folder_id, section_ids, alias_map)

    # add audio/video content to 'Resources' folder
    add_resources(service, chart, chart_id, new_resources_id)

# Main method
def redvest_creator():
    # Build service
    service = util.build_service()

    # Read folder locations
    redvest_options = util.parse_options("redvest_options.json")
    if redvest_options == None: return 1

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    _, current_chartz_id, _ = util.get_digital_library(service)
    if current_chartz_id == None: return 1
    print("Verifying Redvest folder...")
    new_folder_id, new_resources_id = verify_redvest(service, redvest_options)
    if new_folder_id == None or new_resources_id == None: return 1

    # Only make individual section folders if field set to true
    alias_map = None
    section_ids = None
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
    for chart in redvest_options["chartz"]:
        write_song(service, chart, current_chartz_id, new_folder_id, new_resources_id, section_ids, alias_map)
    
    print(f'Successfully created new folder "{redvest_options["folder-name"]}"!')
    return 0
