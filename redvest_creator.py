from login import fetch_credentials
import util
import json, sys
from googleapiclient.discovery import build

# List of acceptable resources
RESOURCES = [".mid", ".mp3", ".mp4", ".mov", ".wav", ".wmv"]

# Verify redvest location and create new class folder
def verify_redvest(service, redvest_options):
    redvest_id = util.get_folder_ids(service, name=redvest_options["parent-name"])[0]
    folder_name = redvest_options["folder-name"]

    # Ensure redvest folder exists
    if len(util.get_folder_ids(service, id=redvest_id)) == 0:
        print('Specified Redvest folder not found Librarianz Drive, please check Google Drive')
        sys.exit(1)

    # See if target folder already exists
    if len(util.get_folder_ids(service, name=folder_name, parent=redvest_id)) > 0:
        print(f'Folder \"{folder_name}\" already exists!')
        print("(You may need to remove the folder from the Trash in the Librarianz Drive)")
        sys.exit(1)

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
    for item in util.get_file_types(service, parts_id, [".pdf"]):
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
    items = util.get_file_types(service, chart_id, RESOURCES)
    
    # Add shortcuts to these resources
    for item in items:
        util.make_shortcut(service, item.get('name'), item.get('id'), new_resources_id)
    
    if len(items) == 0:
        print(f'WARNING: Resource files not found for "{chart}"')

def write_song(service, chart, current_chartz_id, new_folder_id, new_resources_id, section_ids=None, alias_map=None):
    print(f"Writing chart \"{chart}\"...")

    chart_id = util.get_chart_id(service, chart, [current_chartz_id])
    if (chart_id == None): return

    # add shortcut to parts folder
    add_parts_shortcut(service, chart, chart_id, new_folder_id, section_ids, alias_map)

    # add audio/video content to 'Resources' folder
    add_resources(service, chart, chart_id, new_resources_id)

def main():
    # Build service
    creds = fetch_credentials()
    service = build('drive', 'v3', credentials=creds)

    # Read folder locations
    redvest_options = None
    with open("redvest_options.json") as f:
        redvest_options = json.load(f)

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    _, current_chartz_id, _ = util.get_digital_library(service)
    print("Verifying Redvest folder...")
    new_folder_id, new_resources_id = verify_redvest(service, redvest_options)

    # Only make individual section folders if field set to true
    alias_map = None
    section_ids = None
    if redvest_options["individual-sections"] == "True":
        # Read parts
        parts_dict = None
        with open("parts.json") as f:
            parts_dict = json.load(f)
        
        # Make individual section folders
        print("Making individual section folders...")
        section_ids = make_section_folders(service, new_folder_id, parts_dict.keys())

        # Invert parts_dict to create map of alias's -> folder
        alias_map = {}
        for part in parts_dict.keys():
            for alias in parts_dict[part]:
                alias_map[alias] = part

    # Write each chart to the new redvest folder
    for chart in redvest_options["chartz"]:
        write_song(service, chart, current_chartz_id, new_folder_id, new_resources_id, section_ids, alias_map)
    
    print(f'Succesfully created new folder "{redvest_options["folder-name"]}"!')

if __name__ == '__main__':
    main()