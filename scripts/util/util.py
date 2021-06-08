import os, io, sys, json, pickle, re, mimetypes, shutil
from scripts.util.thread_events import check_stop_script
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Value to represent no part
NO_PART = "NO_PART"

# Custom Exception for when credentials fail to load
class CredentialsError(Exception):
    pass

# Returns whether or not the script is running in an exe/frozen file
def is_frozen():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Builds the drive service
def build_service():
    check_stop_script()
    return build('drive', 'v3', credentials=fetch_credentials())

# Fetches the user's credentials, assume credential files are in root directory
def fetch_credentials():
    """Loads the user's credentials from credentials.json or a token
    """
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    res_paths = parse_options('res_paths.json')
    token_path = resourcePath(os.path.join(res_paths['res-path'], 'res/token.pickle'))
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_path = res_paths['creds-path']
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    resourcePath(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
            except (UnicodeDecodeError, ValueError, OSError):
                res_paths['creds-path'] = ''
                write_options(res_paths, 'res_paths.json')
                raise CredentialsError(f'ERROR: Credentials file "{os.path.basename(creds_path)}" invalid. Please restart the application.')

        # Save the credentials for the next run
        with open(resourcePath(token_path), 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Path to resources
def resourcePath(rel_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if is_frozen():
        return os.path.join(getattr(sys, '_MEIPASS', ''), rel_path)
    return rel_path

# Make Application Data files
def make_application_data(data_dir, recopy=False):
    path_exists = os.path.exists(data_dir)
    if path_exists and not recopy: return

    if not path_exists:
        os.makedirs(data_dir)
    
    src = resourcePath("./res")
    shutil.copytree(src, os.path.join(data_dir, 'res'), dirs_exist_ok=True)

    # Remove token.pickle file
    pickle = os.path.join(data_dir, 'res/token.pickle')
    if os.path.isfile(pickle):
        os.remove(pickle)

# Gets the path to the specified location within the resources directory
def get_full_path(partial_path):
    with open(resourcePath('res/options/res_paths.json')) as f:
        res_path = json.load(f)['res-path']

    if (res_path == '' or res_path == '.'):
        return resourcePath(partial_path)
    elif is_frozen():
        return os.path.join(res_path, partial_path)
    else:
        return partial_path

# Write to options json file
def write_options(options, filename, path = "res/options/"):
    full_path = os.path.join(get_full_path(path), filename)
    
    try:
        with open(full_path, 'w') as f:
            json.dump(options, f, indent=4)
    except OSError:
        print(f'ERROR: could not write to file "{full_path}"')

# Parse json options file
def parse_options(filename, path = "res/options/", from_=None):
    if not from_ or not os.path.isdir(from_):
        full_path = os.path.join(get_full_path(path), filename)
    else:
        full_path = os.path.join(from_, path, filename)
    
    try:
        with open(full_path) as f:
            return json.load(f)
    except OSError:
        print(f'ERROR: could not parse file "{full_path}"')
        return None

# Parse title of a file into [chartname, partname (if applicable), mimeType]
def parse_file(filename, alias_map=None):
    # title - part format
    match = re.search('(.*) - (.*)\.(.*)', filename)
    if match:
        return match.group(1), (alias_map.get(match.group(2)) or NO_PART) if alias_map else None, mimetypes.guess_type(filename)[0]


    # other file type format
    match = re.search('(.*)\.[\w+]', filename)
    if match:
        return match.group(1), None, mimetypes.guess_type(filename)[0]
    return None, None, None

# Convert dict of Part Name : [Valid Asiases] to dict of Alias : Part Name
def make_alias_map(parts_dict):
    alias_map = {}
    for part in parts_dict.keys():
        for alias in parts_dict[part]:
            alias_map[alias] = part
    return alias_map

# Gets the desired chart folder, searching in the directories in the id list. Returns a dictionary containing chart id and parent id
def get_chart_id(service, chart, id_list):
    for id in id_list:
        results = service.files().list(corpora="user",
                                       pageSize=1000,
                                       fields="files(id)",
                                       q=f'mimeType = "application/vnd.google-apps.folder" and'
                                         f'"{id}" in parents and '
                                         f'name="{chart}"',
                                       spaces="drive").execute()
        items = results.get('files', [])
        if len(items) == 1:
            return { "chart_id": items[0].get('id'), "parent_id": id }
    
    print(f'ERROR: "{chart}" folder not found in Digital Library directory')
    return { "chart_id": None, "parent_id": None }

# Gets the chart's parts folder, return its id (or None)
def get_parts_and_audio_folders(service, chart, chart_id):
    output = []
    for folder_name in ("Parts", "Audio"):
        # Search for parts folder
        folder_results = service.files().list(corpora="user",
                                            fields="files(id)",
                                            pageSize=1000,
                                            q=f'mimeType = "application/vnd.google-apps.folder" and'
                                            f'"{chart_id}" in parents and'
                                            f'name="{folder_name}"',
                                            spaces="drive").execute()
        items = folder_results.get('files', [])
        if len(items) != 1:
            print(f"ERROR: {folder_name} folder not found for current chart with name:", chart)
            output.append(None)
        else:
            output.append(items[0].get('id'))
    
    return tuple(output)

# Creates a folder
def make_folder(service, name, parent, makePublic=False):

    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent]
    }
    try:
        response = service.files().create(body=file_metadata, fields='id').execute()
        folderId = response.get('id')
        if makePublic:
            service.permissions().create(fileId=folderId, body={'type': 'anyone', 'role': 'reader'})
        return response.get('id')
    except HttpError:
        print(f'ERROR: Unable to create folder "{name}"')
        return None

# Moves a file (or folder)
def move_file(service, file_id, old_parent, new_parent):
    try:
        service.files().update(fileId=file_id,
                                addParents=new_parent,
                                removeParents=old_parent,
                                fields='id, parents').execute()
    except HttpError:
        print(f'ERROR: Unable to move file')

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
# Modified to work with v3 api
def update_file(service, file_id, new_filename, new_title=None, new_description=None, new_mime_type=None):
    try:
        # First retrieve the file from the API.
        file = service.files().get(fileId=file_id).execute()

        # File's new metadata.
        del file["id"]
        if (new_title): file['title'] = new_title
        if (new_description): file['description'] = new_description
        if (new_mime_type): file['mimeType'] = new_mime_type

        # File's new content.
        media_body = MediaFileUpload(new_filename, mimetype=new_mime_type, resumable=True)

        # Send the request to the API.
        updated_file = service.files().update(
            fileId=file_id,
            body=file,
            media_body=media_body,
            fields='id').execute()
        return updated_file["id"]
    except HttpError:
        print(f'Error when attempting to update file: {new_filename}')
        return None

# Upload a file to a folder in the drive
def upload_file(service, new_filename, display_name, parent, title=None, mime_type=None):
    try:
        # Create file metadata
        file_metadata = {
            'name' : display_name,
            'parents': [parent]
        }
        if title: file_metadata['title'] = title
        if mime_type: file_metadata['mimeType'] = mime_type

        # Make the file
        media = MediaFileUpload(new_filename, mimetype=mime_type)
        return service.files().create(body=file_metadata, media_body=media, fields='id').execute().get('id')
    except HttpError:
        print(f'WARNING: Unable to create file "{display_name}"')
        return None

# Downloads a file (or folder) from the drive
def download_file(service, file_id, dir, file_name, verbose=False):
    try:
        # Get target file
        request = service.files().get_media(fileId=file_id)

        # Resolve destination
        if not os.path.exists(dir): os.makedirs(dir)
        fh = io.FileIO(os.path.join(dir, file_name), "w")

        # Execute download
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        if verbose: print(f'Starting download of "{file_name}"')
        while done is False:
            status, done = downloader.next_chunk()
            if verbose: print(f'Progress: {status.progress() * 100}%')
        if verbose: print("Completed download")
    except (OSError, HttpError):
        print(f'WARNING: Unable to download "{file_name}"')

# Returns the id(s) of a folder with the given id or name (optionally can specify parent directory)
def get_folder_ids(service, id = None, name = None, parent = None):
    # Check folder by id
    if (id != None):
        res = service.files().get(fileId=id, fields="id").execute()
        if res.get("id") and res["id"] == id: return [id]
        return None
    
    if (name == None): return None

    # Check folder by name + parent (optional) 
    qstring = f'name="{name}" and mimeType="application/vnd.google-apps.folder"'
    if (parent != None): qstring += f' and "{parent}" in parents'

    results = service.files().list(q=qstring,
                                    corpora='user',
                                    pageSize=1000,
                                    fields='files(id)',
                                    includeItemsFromAllDrives=True,
                                    supportsAllDrives=True).execute()
    return [ res.get("id") for res in results.get("files") ] if results.get("files") else None

# Verify and return the digital library
def get_digital_library(service):
    """Verify that the DigitalLibrary folder and subfolders are in the correct locations.
    """
    check_stop_script()
    library_id, full_dig_id, current_id, future_id, archive_id = None, None, None, None, None

    # DigitalLibrary folder
    library_res = get_folder_ids(service, name="DigitalLibrary", parent="root")
    if not has_unique_folder(library_res, "DigitalLibrary", "My Drive"): return {}
    library_id = library_res[0]

    # Digitized Chart Data folder
    full_dig_res = get_folder_ids(service, name="LSJUMB Full Digitized Chart Data", parent=library_id)
    if not has_unique_folder(full_dig_res, "LSJUMB Full Digitized Chart Data", "DigitalLibrary"): return {}
    full_dig_id = full_dig_res[0]

    # Current Chartz folder
    current_res = get_folder_ids(service, name="Current Chartz", parent=full_dig_id)
    if not has_unique_folder(current_res, "Current Chartz", "LSJUMB Full Digitized Chart Data"): return {}
    current_id = current_res[0]

    # Old Chartz folder
    past_res = get_folder_ids(service, name="Old Chartz", parent=full_dig_id)
    if not has_unique_folder(past_res, "Old Chartz", "LSJUMB Full Digitized Chart Data"): return {}
    past_id = past_res[0]

    # Future Chartz folder
    future_res = get_folder_ids(service, name="Future Chartz", parent=full_dig_id)
    if not has_unique_folder(future_res, "Future Chartz", "LSJUMB Full Digitized Chart Data"): return {}
    future_id = future_res[0]

    # Archived Chartz folder
    archive_res = get_folder_ids(service, name="Archived Chartz", parent=full_dig_id)
    if not has_unique_folder(archive_res, "Archived Chartz", "LSJUMB Full Digitized Chart Data"): return {}
    archive_id = archive_res[0]

    return {"library_id": library_id, "current_id": current_id, "past_id": past_id, "future_id": future_id, "archive_id": archive_id}

# Get seperated section or separated sibelius parts folders
def get_separated_folders(service, library_id):
    check_stop_script()
    separated_ids = {}
    folder_names = [("Separated Sibelius Files", "sib"), ("Separated Section Parts", "sec"), ("Separated Part Audio", "aud")]
    for folder_name, abbr in folder_names:
        # Look for folder within Digital Library
        ids = get_folder_ids(service, name=folder_name, parent=library_id)
        if not has_unique_folder(ids, folder_name, "Digital Library"): return None       
        separated_ids[abbr] = ids[0]

        # Look for Current, Old, Future, Archived Chartz folders
        for age_name, age in [("Current Chartz", "curr"), ("Old Chartz", "old"), ("Future Chartz", "future")]:
            age_ids = get_folder_ids(service, name=age_name, parent=ids[0])
            if not has_unique_folder(age_ids, age_name, folder_name): return None
            separated_ids[f'{abbr}_{age}'] = age_ids[0]

    
    return separated_ids

# Search folder for specific files/folders
def get_drive_files(service, id, file_types=None, files_only=True, folders_only=False, name=None, is_shortcut=False):
    output = []
    q = f'"{id}" in parents'
    if files_only: q += ' and not mimeType = "application/vnd.google-apps.folder"'
    if folders_only: q += ' and mimeType = "application/vnd.google-apps.folder"'
    if name: q += f' and name contains "{name}"'

    fields = f'files(id, name{", shortcutDetails" if is_shortcut else ""})'

    # Get all files/folders in the folder
    file_results = service.files().list(corpora="user",
                                        pageSize=1000,
                                        fields=fields,
                                        q=q,
                                        spaces="drive").execute()
    items = file_results.get('files', [])

    # Check that file extensions match
    for item in items:
        if not file_types or item.get('name')[-4:] in file_types:
            output.append(item)
    
    return output

# Return list of files in a given directory with a specific extension
def get_dir_files(dir, file_types):
    try:
        files = [ file for file in os.listdir(dir) if file[-4:] in file_types ]
        if len(files) == 0: raise OSError
        return files
    except OSError:
        print(f'ERROR: No supported files found in directory "{dir}"')
        sys.exit()

# A helper function that outputs some useful error messages
def has_unique_folder(res, target, parent):
    if res == None or len(res) == 0:
        print(f'ERROR: "{target}" folder not found in "{parent}" directory, please check Google Drive')
        return False
    elif len(res) > 1:
        print(f'ERROR: Multiple instances of "{target}" folder found in "{parent}" directory, please check Google Drive')
        print(f'Double-check the Trash section of Google Drive, as it still belongs to the "{parent}" folder')
        return False
    else:
        return True