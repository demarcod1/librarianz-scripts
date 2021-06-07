from scripts.util.permissions_utils import get_file_permissions, public_id, should_be_private, should_be_public
import scripts.util.util as util
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
    audio_id = cache[chart]["audio_id"]
    loc_raw = cache[chart]["loc"]
    if not chart_id or not parts_id or loc_raw == None: return False
    loc = "curr" if loc_raw == 0 else "old" if loc_raw == 1 else "future" if loc_raw == 2 else "archived"
    sep_sec_id = separated_ids[f'sec_{loc}']
    sep_sib_id = separated_ids[f'sib_{loc}']
    sep_aud_id = separated_ids[f'aud_{loc}']

    # See if this file already exists
    for file in cache[chart]["files"]:
        if file.get("name") == file_name:
            print(f'ERROR: File with name "{file_name}" already exists!')
            return False
    
    ensure_public = should_be_public(file_name)
    ensure_private = should_be_private(file_name)

    # Add parts or part audio files to the Parts/Audio folder and create a shortcut
    if part:
        upload_dest = None
        sep_dest_parent = None
        sep_dest_title = "None"

        if mimeType == 'application/pdf' or file_name.endswith('.pdf'):
            upload_dest = parts_id
            sep_dest_parent = sep_sec_id
            sep_dest_title = "Separated Section Parts"
        elif mimeType.startswith('audio'):
            upload_dest = audio_id
            sep_dest_parent = sep_aud_id
            sep_dest_title = "Separated Part Audio"
        else:
            print(f'ERROR: Unable to categorize part file "{file_name}"')
            return False
        
        file_id = util.upload_file(service, os.path.join(directory, file_name), file_name, upload_dest, mime_type=mimeType)
        if part == util.NO_PART:
            print(f'WARNING: No matching part found for "{file_name}"')
            return True
        sep_dest_ids = util.get_folder_ids(service, name=part, parent=sep_dest_parent)
        if sep_dest_ids == None:
            print(f'WARNING: Unable to create shortcut in {sep_dest_title} for "{file_name}"')
        elif loc != "archived": # Don't make shortcuts for archived files
            util.make_shortcut(service, file_name, file_id, sep_dest_ids[0])

        # Update permissions, if needed
        permission_id = public_id(get_file_permissions(service, file_id))
        if permission_id and ensure_private:
            print("Was public, should be private")
            service.permissions().delete(fileId=file_id, permissionId=permission_id).execute()
        if not permission_id and ensure_public:
            service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()
        return True
    
    # Add other files to the chart's main folder
    file_id = util.upload_file(service, os.path.join(directory, file_name), file_name, chart_id, mime_type=mimeType)
    if (file_name.endswith('.sib')):
        util.make_shortcut(service, file_name, file_id, sep_sib_id)
    
    # Update permissions, if needed
    permission_id = public_id(get_file_permissions(service, file_id))
    if permission_id and ensure_private:
        service.permissions().delete(fileId=file_id, permissionId=permission_id).execute()
    if not permission_id and ensure_public:
        service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()

    return True

# Creates a new directory + parts folder for a new chart to be housed
def create_chart_structure(service, chartz_id, chart_name):
    # Ensure this chart doesn't already exist!
    if util.get_folder_ids(service, name=chart_name, parent=chartz_id) != None:
        print(f'WARNING: Chart with name "{chart_name}" already exists, no new folder will be created')
        return None, None
    
    # Create new chart folder
    chart_id = util.make_folder(service, chart_name, chartz_id)
    parts_id = util.make_folder(service, "Parts", chart_id, True)
    audio_id = util.make_folder(service, "Audio", chart_id, True)
    print(f'Successfully created chart folder for "{chart_name}"')
    return chart_id, parts_id, audio_id

# Populates the cache with all the relevant information about the specific chart
def populate_cache(service, curr_id, old_id, future_id, archive_id, chart, cache, options):
    try:
        # Find this chart's folder id
        res = util.get_chart_id(service, chart, [curr_id, old_id, future_id, archive_id])
        if not res: raise RuntimeError
        chart_id = res.get("chart_id")
        if chart_id == None: raise RuntimeError
        
        # Determine whether the chart is in the "current chartz", "future chartz", or "old chartz" folder
        parent_id = res.get("parent_id")
        loc = 0 if curr_id == parent_id else 1 if old_id == parent_id else 2 if future_id == parent_id else 3

        # Find this chart's parts foler id
        parts_id, audio_id = util.get_parts_and_audio_folders(service, chart, chart_id)
        if parts_id == None or audio_id == None: raise RuntimeError
        
        # Populate cache with this chart's data
        cache[chart] = { "chart_id": chart_id, "loc": loc, "parts_id": parts_id, "audio_id": audio_id, "files": [] }
        cache[chart]["files"] = util.get_drive_files(service, chart_id, options["supported-file-types"])
        cache[chart]["files"].extend(util.get_drive_files(service, parts_id, options["supported-file-types"]))
        cache[chart]["files"].extend(util.get_drive_files(service, audio_id, options["supported-file-types"]))
    except RuntimeError:
        cache[chart] = { "chart_id": None, "loc": None, "parts_id": None, "audio_id": None, "files": []}

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
        print(f'WARNING: No files found for "{chart}" in the Digital Library')
        return False

    for file in files:
        # if part field is non-null, we can also check that aliases match up
        if file.get("name") == filename or (not titles_match and part and
                                            util.parse_file(file.get("name"), alias_map)[1] == part):
            if(util.update_file(service, file.get("id"), os.path.join(directory, filename), new_mime_type=mimeType)):
                return True
    return False