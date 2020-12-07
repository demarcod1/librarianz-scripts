from os import name
from scripts.util.thread_events import check_stop_script
from typing import Dict
import  scripts.util.util as util

# Make a new seperated parts substructure
def new_sep_structure(service, sep_sec_id, sep_sib_id, parts_dict: Dict):
    # Create new "Current Chartz" and "Old Chartz" separated section part folders
    output = {}

    for parent, abbr in [(sep_sec_id, 'sec'), (sep_sib_id, 'sib')]:
        for prefix, age in [("Current", 'curr'), ("Old", 'old')]:
            res = util.make_folder(service, f'{prefix} Chartz', parent)
            if not res: return None
            output[f'sep_{abbr}_{age}'] = res

    # Create individual part folders
    for age in ('old', 'curr'):
        output[age] = {}
        for part in parts_dict.keys():
            res = util.make_folder(service, part, output[f'sep_sec_{age}'])
            if not res: return None
            output[age][part] = res
    
    return output

# Returns a dictionary containing the names and ids of all the chartz in the Digital Library
def get_all_chart_folders(service, curr_id, old_id, future_id):
    output = {}

    # Get every chart folder per age group
    for parent, age in [(curr_id, 'curr'), (old_id, 'old'), (future_id, 'future')]:
        check_stop_script()
        output[age] = {}
        res = util.get_drive_files(service, parent, files_only=False, folders_only=True)
        for item in res:
            output[age][item.get('name')] = item.get('id')
    
    return output

# Writes a chart's shortcut out to the new separated folders
def write_shortcuts(service, chartname, id, age, new_folders, alias_map):
    # Find the sibelius file
    check_stop_script()
    res = util.get_drive_files(service, id, ['.sib'])
    if not res or len(res) == 0:
        print(f'WARNING: Could not find Sibelius file for chart "{chartname}"')
    else:
        if len(res) > 1:
            print(f'WARNING: Multiple Sibelius files found for chart "{chartname}". The first one seen will be used in the shortcut.')
        util.make_shortcut(service, res[0].get('name'), res[0].get('id'), new_folders[f'sep_sib_{age}'])
    
    # Find the chart's Parts folder
    check_stop_script()
    parts_id = util.get_parts_folder(service, chartname, id)
    if not parts_id: return

    # Create a shortcut for each part in the Parts folder
    res = util.get_drive_files(service, parts_id, ['.pdf'])
    if not res or len(res) == 0:
        print(f'ERROR: No parts files found for chart "{chartname}"')
        return
    
    for partfile in res:
        # Ensure part exists in the system
        check_stop_script()
        partfile_name = partfile.get('name')
        _, part, _ = util.parse_file(partfile_name, alias_map)
        if part == None:
            print(f'WARNING: Part file "{partfile_name}" has no matching part folder')
            continue
        
        # Make the shortcut
        util.make_shortcut(service, partfile_name, partfile.get('id'), new_folders[age][part])

# Gets the id of the 'LSJUMB Digital Chartz'
def get_lsjumb_digital_chartz_id(service, library_id):
    # Find "[LIVE] DigitalLibrary" folder
    check_stop_script()
    res = util.get_folder_ids(service, name="[LIVE] DigitalLibrary", parent=library_id)
    if not res or len(res) != 1:
        print('ERROR: Unable to find "[LIVE] DigitalLibrary" directory in "DigitalLibrary"')
        return None
    live_dig_lib_id = res[0]

    # Find (and return) "LSJUMB Digital Chartz" folder
    res = util.get_folder_ids(service, name="LSJUMB Digital Chartz", parent=live_dig_lib_id)
    if not res or len(res) != 1:
        print('ERROR: Unable to find "LSJUMB Digital Chartz" directory in "[LIVE] DigitalLibrary"')
        return None
    return res[0]

# Returns the id's of the existing "Current Chartz" and "Old Chartz" folders in the live library
def get_curr_old_live_ids(service, live_id):
    curr_id = None
    old_id = None

    res = util.get_folder_ids(service, name="Current Chartz", parent=live_id)
    if res and len(res) == 1:
        curr_id = res[0]
    else:
        print('WARNING: Unable to find unique "Current Chartz" folder in "LSJUMB Digital Chartz" directory')
    
    res = util.get_folder_ids(service, name="Old Chartz", parent=live_id)
    if res and len(res) == 1:
        old_id = res[0]
    else:
        print('WARNING: Unable to find unique "Old Chartz" folder in "LSJUMB Digital Chartz" directory')
    
    return curr_id, old_id

# Adds the relevant parts shortcuts to the live digital library
def add_live_part_shortcuts(service, live_id, age, new_folders, exclude):
    for part in new_folders[age]:
        check_stop_script()
        if part in exclude:
            print(f'WARNING: Part "{part}" will be excluded from the Live Digital Library')
            continue
        util.make_shortcut(service, part, new_folders[age][part], live_id)

# Adds new "Current Chartz" and "Old Chartz" folders to the live library
def add_live_part_folders(service, live_id):
    return util.make_folder(service, "Current Chartz", live_id), util.make_folder(service, "Old Chartz", live_id)

# Deletes the list of ids
def delete_files(service, ids):
    for id in ids:
        if not id: continue
        service.files().delete(fileId=id).execute()
