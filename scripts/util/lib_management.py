from . import util
import os

# Adds a file to the library, also adding shortcuts to separated sib files/section parts if needed
def add_file(service, file_name, separated_ids, alias_map, cache, options):
    # Parse file and options information
    directory = options["resources-directory"]
    chart, part, mimeType = util.parse_file(file_name, alias_map)

    # See if cache contains necessary information
    if not chart in cache: return False
    chart_id = cache[chart]["chart_id"]
    parts_id = cache[chart]["parts_id"]
    current = cache[chart]["is_current"]
    if not chart_id or not parts_id or current == None: return False
    sep_sec_id = separated_ids[f'sec_{"curr" if current else "old"}']
    sep_sib_id = separated_ids[f'sib_{"curr" if current else "old"}']

    # See if this file already exists
    for file in cache[chart]["files"]:
        if file.get("name") == file_name:
            print(f'WARNING: File with name "{file_name}" already exists!')
            return False
    
    # Add parts files to the Parts folder and create a shortcut
    if part:
        file_id = util.upload_file(service, os.path.join(directory, file_name), file_name, parts_id, mime_type=mimeType)
        sep_part_ids = util.get_folder_ids(service, name=part, parent=sep_sec_id)
        if len(sep_part_ids) != 1:
            print(f'WARNING: Unable to create shortcut in Separated Section Parts for "{file_name}"')
        else: util.make_shortcut(service, file_name, file_id, sep_part_ids[0])
        return True
    
    # Add other files to the chart's main folder
    file_id = util.upload_file(service, os.path.join(directory, file_name), file_name, chart_id, mime_type=mimeType)
    if (file_name.endswith('.sib')):
        util.make_shortcut(service, file_name, file_id, sep_sib_id)
    return True

# Creates a new directory + parts folder for a new chart to be housed
def create_chart_structure(service, chartz_id, chart_name):
    # Ensure this chart doesn't already exist!
    if len(util.get_folder_ids(service, name=chart_name, parent=chartz_id)) > 0:
        print(f'WARNING: Chart with name "{chart_name}" already exists, no new folder will be created')
        return None, None
    
    # Create new chart folder
    chart_id = util.make_folder(service, chart_name, chartz_id)
    parts_id = util.make_folder(service, "Parts", chart_id)
    print(f'Successfully created chart folder for "{chart_name}"')
    return chart_id, parts_id

# Populates the cache with all the relevant information about the specific file
def populate_cache(service, curr_id, old_id, chart, cache, options):
    try:
        # Find this chart's folder id
        res = util.get_chart_id(service, chart, [curr_id, old_id])
        if not res: raise Exception
        chart_id = res.get("chart_id")
        if chart_id == None: raise Exception
        
        # Determine whether the chart is in the "current chartz" or "old chartz" folder
        is_current = curr_id == res.get("parent_id")

        # Find this chart's parts foler id
        parts_id = util.get_parts_folder(service, chart, chart_id)
        if parts_id == None: raise Exception
        
        # Populate cache with this chart's data
        cache[chart] = { "chart_id": chart_id, "is_current": is_current, "parts_id": parts_id, "files": [] }
        cache[chart]["files"] = util.get_drive_files(service, chart_id, options["supported-file-types"])
        cache[chart]["files"].extend(util.get_drive_files(service, parts_id, options["supported-file-types"]))
    except:
        cache[chart] = { "chart_id": None, "is_current": None, "parts_id": None, "files": []}

# Update the file with the specified path, return whether the update was successful
def update_file(service, filename, alias_map, cache, options):
    # parse file and options
    directory = options["resources-directory"]
    titles_match = options["require-titles-match"]
    chart, part, mimeType = util.parse_file(filename, alias_map)

    # Retrieve updatable files
    if not chart in cache or not "files" in cache[chart]:
        print(f'WARNING: No cache entry found for "{chart}"')
        return False
    files = cache.get(chart).get('files')
    if not files or len(files) == 0:
        print(f'WARNING: No files found for "{chart}"')
        return False

    for file in files:
        # if part field is non-null, we can also check that aliases match up
        if file.get("name") == filename or (not titles_match and part and
                                            util.parse_file(file.get("name"), alias_map)[1] == part):
            if(util.update_file(service, file.get("id"), os.path.join(directory, filename), new_mime_type=mimeType)):
                return True
    return False