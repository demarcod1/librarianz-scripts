from .login import fetch_credentials
from .util.util import get_digital_library, parse_options
from googleapiclient.discovery import build

def delete_existing_directory(service, library_id):
    """Deletes previously-created shortcuts from prior run.
    NOTE: this is unnecessary and could be cut out/made more efficiently later if desired."""
    try:
        results = service.files().list(corpora="user",
                                       fields="files(id, name)",
                                       q=f'mimeType = "application/vnd.google-apps.folder" and'
                                         f'"{library_id}" in parents and '
                                         f'name="Separated Section Parts"',
                                       spaces="drive").execute()
        items = results.get('files', [])
        if len(items) != 1:
            raise Exception()
        service.files().delete(fileId=items[0].get('id')).execute()
    except:
        print('"Separated Section Parts" folder not found, skipping deletion.')

    try:
        results = service.files().list(corpora="user",
                                       fields="files(id, name)",
                                       q=f'mimeType = "application/vnd.google-apps.folder" and'
                                         f'"{library_id}" in parents and '
                                         f'name="Separated Sibelius Files"',
                                       spaces="drive").execute()
        items = results.get('files', [])
        if len(items) != 1:
            raise Exception()
        service.files().delete(fileId=items[0].get('id')).execute()
    except:
        print('"Separated Sibelius Files" folder not found, skipping deletion.')

def create_directories(service, library_id, parts_dict):
    """Creates all directories to sort charts and sibelius files into.
    """

    # master folder for separated section parts
    file_metadata = {
        'name': 'Separated Section Parts',
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [library_id]
    }
    response = service.files().create(body=file_metadata, fields='id').execute()
    parts_id = response.get('id')

    # master folder for separated sibelius files
    file_metadata = {
        'name': 'Separated Sibelius Files',
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [library_id]
    }
    response = service.files().create(body=file_metadata, fields='id').execute()
    sib_id = response.get('id')

    # folder for current separated parts
    file_metadata = {
        'name': "Current Chartz",
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parts_id]
    }
    response = service.files().create(body=file_metadata, fields='id').execute()
    curr_chart_out_id = response.get('id')

    # folder for old separated parts
    file_metadata = {
        'name': "Old Chartz",
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parts_id]
    }
    response = service.files().create(body=file_metadata, fields='id').execute()
    past_chart_out_id = response.get('id')

    # folder for current sibelius files
    file_metadata = {
        'name': "Current Chartz",
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [sib_id]
    }
    response = service.files().create(body=file_metadata, fields='id').execute()
    curr_sib_out_id = response.get('id')

    # folder for old sibelius files
    file_metadata = {
        'name': "Old Chartz",
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [sib_id]
    }
    response = service.files().create(body=file_metadata, fields='id').execute()
    old_sib_out_id = response.get('id')

    section_curr_outputs = {}
    for part in parts_dict:
        file_metadata = {
            'name': part,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [curr_chart_out_id]
        }
        response = service.files().create(body=file_metadata, fields='id').execute()
        part_id = response.get('id')
        for alias in parts_dict[part]:
            section_curr_outputs[alias] = part_id

    section_old_outputs = {}
    for part in parts_dict:
        file_metadata = {
            'name': part,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [past_chart_out_id]
        }
        response = service.files().create(body=file_metadata, fields='id').execute()
        part_id = response.get('id')
        for alias in parts_dict[part]:
            section_old_outputs[alias] = part_id

    return section_curr_outputs, section_old_outputs, curr_sib_out_id, old_sib_out_id

def write_song_parts_out(service, parts_folder, section_out, name):
    """Helper function to write out the parts for a given song to their respective folders.
    """
    part_results = service.files().list(corpora="user",
                                        fields="files(id, name)",
                                        q=f'"{parts_folder}" in parents',
                                        spaces="drive").execute()
    items = part_results.get('files', [])
    for item in items:
        if item.get('name')[-4:] == '.pdf':
            part = item.get('name').split('-')[-1].strip()[:-4]
            out_folder = section_out.get(part)
            if not out_folder:
                print("WARNING: Chart with folder name", name, "contains part", part, "with no output folder, consider "
                                                                                      "configuring parts.json")
                continue
            shortcut_metadata = {
                'name': item.get('name'),
                'mimeType': 'application/vnd.google-apps.shortcut',
                'shortcutDetails': {
                    'targetId': item.get('id')
                },
                'parents': [out_folder]
            }
            service.files().create(body=shortcut_metadata).execute()

def write_song_out(service, chart_folder, section_out, sibelius_out, name):
    """Helper function to write the sibelius files for a song out to the proper folder and dispatch
    writing section parts out to a helper function."""
    folder_results = service.files().list(corpora="user",
                                        fields="files(id, name)",
                                        q=f'mimeType = "application/vnd.google-apps.folder" and'
                                          f'"{chart_folder}" in parents and'
                                          f'name="Parts"',
                                        spaces="drive").execute()
    items = folder_results.get('files', [])
    if len(items) != 1:
        print("WARNING: Single parts folder not found for current chart with name:", name)
    else:
        write_song_parts_out(service, items[0].get('id'), section_out, name)

    # search root folder for sibelius files and create shortcuts
    file_results = service.files().list(corpora="user",
                                        fields="files(id, name)",
                                        q=f'not mimeType = "application/vnd.google-apps.folder" and'
                                          f'"{chart_folder}" in parents',
                                        spaces="drive").execute()
    items = file_results.get('files', [])
    if len(items) == 0:
        print("WARNING: Sibelius files not found for current chart with name:", name)
    for item in items:
        if item.get('name')[-4:] == '.sib':
            shortcut_metadata = {
                'name': item.get('name'),
                'mimeType': 'application/vnd.google-apps.shortcut',
                'shortcutDetails': {
                    'targetId': item.get('id')
                },
                'parents': [sibelius_out]
            }
            service.files().create(body=shortcut_metadata).execute()

def build_shortcuts(service, curr_chart_in, old_chart_in, curr_sec_out, old_sec_out, curr_sib_out, old_sib_out):
    """Function that controls building shortcut outputs that adhere to the new structure for current
    and old charts."""
    results = service.files().list(corpora="user",
                                   fields="files(id, name)",
                                   q=f'mimeType = "application/vnd.google-apps.folder" and'
                                     f'"{curr_chart_in}" in parents',
                                   spaces="drive").execute()
    items = results.get('files', [])
    for item in items:
        print("Writing song:", item.get('name'))
        write_song_out(service, item.get('id'), curr_sec_out, curr_sib_out, item.get('name'))

    results = service.files().list(corpora="user",
                                   fields="files(id, name)",
                                   q=f'mimeType = "application/vnd.google-apps.folder" and'
                                     f'"{old_chart_in}" in parents',
                                   spaces="drive").execute()
    items = results.get('files', [])
    for item in items:
        print("Writing song:", item.get('name'))
        write_song_out(service, item.get('id'), old_sec_out, old_sib_out, item.get('name'))

# Main method
def separated_folders_creator():
    print("This script has been disabled")
    return 1
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = fetch_credentials()
    service = build('drive', 'v3', credentials=creds)

    parts_dict = parse_options("parts.json")
    if parts_dict == None: return 1

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    library_id, current_chartz_id, old_chartz_id = get_digital_library(service)
    if library_id == None: return 1

    # Delete output from prior runs to avoid side effects
    print("Deleting old output...")
    delete_existing_directory(service, library_id)

    # Create all directories for outputting files
    print("Creating output folders...")
    curr_sec_out, old_sec_out, curr_sib_out, old_sib_out = create_directories(service, library_id, parts_dict)

    # curr_sec_out, old_sec_out, curr_sib_out, old_sib_out = None, None, None, None
    # Builds shortcuts for all songs to the newly generated folders
    print("Writing output...")
    build_shortcuts(service, current_chartz_id, old_chartz_id, curr_sec_out, old_sec_out, curr_sib_out, old_sib_out)

    return 0
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['name'], item['id']))
