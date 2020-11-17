import sys
from apiclient import errors
from apiclient.http import MediaFileUpload

# Gets the desired chart folder, searching in the directories in the id list
def get_chart_id(service, chart, id_list):
    for id in id_list:
        results = service.files().list(corpora="user",
                                       fields="files(id)",
                                       q=f'mimeType = "application/vnd.google-apps.folder" and'
                                         f'"{id}" in parents and '
                                         f'name="{chart}"',
                                       spaces="drive").execute()
        items = results.get('files', [])
        if len(items) == 1:
            return items[0].get('id')
    
    print(f'WARNING: "{chart}" folder not found in Digital Library directory')
    return None

# Gets the chart's parts folder, return its id (or None)
def get_parts_folder(service, chart, chart_id):
    # Search for parts folder
    folder_results = service.files().list(corpora="user",
                                        fields="files(id)",
                                        q=f'mimeType = "application/vnd.google-apps.folder" and'
                                          f'"{chart_id}" in parents and'
                                          f'name="Parts"',
                                        spaces="drive").execute()
    items = folder_results.get('files', [])
    if len(items) != 1:
        print("WARNING: Single parts folder not found for current chart with name:", chart)
        return None
    return items[0].get('id')

# Creates a folder
def make_folder(service, name, parent):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent]
    }
    response = service.files().create(body=file_metadata, fields='id').execute()
    return response.get('id')

# Creates a shortcut
def make_shortcut(service, name, target_id, parent):
    shortcut_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.shortcut',
        'shortcutDetails': {
            'targetId': target_id
        },
        'parents': [parent]
    }
    service.files().create(body=shortcut_metadata).execute()

# Update an existing file's metadata and content.
# Based on: https://developers.google.com/drive/api/v2/reference/files/update
def update_file(service, file_id, new_filename, new_title=None, new_description=None, new_mime_type=None,
                 new_revision=True):
    try:
        # First retrieve the file from the API.
        file = service.files().get(fileId=file_id).execute()

        # File's new metadata.
        if (new_title): file['title'] = new_title
        if (new_description): file['description'] = new_description
        if (new_mime_type): file['mimeType'] = new_mime_type

        # File's new content.
        media_body = MediaFileUpload(new_filename, mimetype=new_mime_type, resumable=True)

        # Send the request to the API.
        updated_file = service.files().update(
            fileId=file_id,
            body=file,
            newRevision=new_revision,
            media_body=media_body,
            fields='id').execute()
        return updated_file["id"]
    except:
        print(f'Unable to update file: {new_filename}')
        return None

# Returns the id(s) of a folder with the given id or name (optionally can specify parent directory)
def get_folder_ids(service, id = None, name = None, parent = None):
    # Chech folder by id
    if (id != None):
        res = service.files().get(fileId=id, fields="id").execute()
        if res["id"] and res["id"] == id: return [id]
        return None
    
    if (name == None): return None

    # Check folder by name + parent (optional) 
    qstring = f'name="{name}" and mimeType="application/vnd.google-apps.folder"'
    if (parent != None): qstring += f' and "{parent}" in parents'

    results = service.files().list(q=qstring,
                                    corpora='user',
                                    fields='files(id)',
                                    includeItemsFromAllDrives=True,
                                    supportsAllDrives=True).execute()
    return [ res.get("id") for res in results["files"] ]

# Verify and return the digital library
def get_digital_library(service):
    """Verify that the DigitalLibrary folder and subfolders are in the correct locations.
    """
    library_id, full_dig_id, current_id, past_id = None, None, None, None

    # DigitalLibrary folder
    library_res = get_folder_ids(service, name="DigitalLibrary", parent="root")
    if (not library_res or len(library_res) != 1):
        print('"DigitalLibrary" folder not found in root Drive directory, please check Google Drive')
        sys.exit(1)
    library_id = library_res[0]

    # Digitized Chart Data folder
    full_dig_res = get_folder_ids(service, name="LSJUMB Full Digitized Chart Data", parent=library_id)
    if (not full_dig_res or len(full_dig_res) != 1):
        print('"LSJUMB Full Digitized Chart Data" folder not found in "DigitalLibrary" directory, please check Google Drive')
        sys.exit(1)
    full_dig_id = full_dig_res[0]

    # Current Chartz folder
    current_res = get_folder_ids(service, name="Current Chartz", parent=full_dig_id)
    if (not current_res or len(current_res) != 1):
        print('"Current Chartz" folder not found in "LSJUMB Full Digitized Chart Data" directory, please check Google Drive')
        sys.exit(1)
    current_id = current_res[0]

    # Old Chartz folder
    past_res = get_folder_ids(service, name="Old Chartz", parent=full_dig_id)
    if (not past_res or len(past_res) != 1):
        print('"Old Chartz" folder not found in "LSJUMB Full Digitized Chart Data" directory, please check Google Drive')
        sys.exit(1)
    past_id = past_res[0]

    return library_id, current_id, past_id

# Search folder for specific file endings
def get_file_types(service, id, file_types):
    output = []
    # Get all files in the folder
    file_results = service.files().list(corpora="user",
                                        fields="files(id, name)",
                                        q=f'not mimeType = "application/vnd.google-apps.folder" and'
                                          f'"{id}" in parents',
                                        spaces="drive").execute()
    items = file_results.get('files', [])

    # Add shortcuts to these resources
    for item in items:
        if item.get('name')[-4:] in file_types:
            output.append(item)
    
    return output