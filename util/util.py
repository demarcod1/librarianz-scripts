import os, sys, json, pickle, re, mimetypes
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from apiclient import errors
from apiclient.http import MediaFileUpload

# Builds the drive service
def build_service():
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
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Parse json options file
def parse_options(filename, path = "options/"):
    try:
        with open(f'{path}{filename}') as f:
            return json.load(f)
    except:
        print(f'ERROR: could not parse file "{path}{filename}"')
        sys.exit()

# Parse title of a file into [chartname, partname (if applicable), mimeType]
def parse_file(filename, alias_map):
    # pdf part format
    match = re.search('(.*) - (.*).pdf', filename)
    if match:
        return match.group(1), alias_map[match.group(2)], mimetypes.guess_type(filename)[0]
    
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
    except:
        print(f'Error when attempting to update file: {new_filename}')
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