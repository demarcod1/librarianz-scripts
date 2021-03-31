from scripts.util.thread_events import check_stop_script

# List of editables - Sibelius, XML, Musescore, and MIDI files
PRIVATE = [".sib", ".xml", ".mscz", ".mid"]

# List of public files - these will always be visible
PUBLIC = [".pdf", ".aiff", ".mp3", ".wav", ".m4a"]

# Returns the permissions list for a file with a certain id
def get_file_permissions(service, file_id):
    return service.permissions().list(fileId=file_id).execute().get('permissions')

# Returns a dictionary of chart name to (id, permissions)
def get_all_chart_permissions(service, curr_id, old_id, future_id):
    output = {}

    # Get every chart folder per age group
    for parent in [curr_id, old_id, future_id]:
        check_stop_script()
        res = service.files().list(corpora="user",
                                   pageSize=1000,
                                   fields="files(id, name, permissions)",
                                   q=f'mimeType = "application/vnd.google-apps.folder" and'
                                     f'"{parent}" in parents',
                                   spaces="drive").execute()
        for entry in res.get('files'):
            output[entry.get('name')] = (entry.get('id'), entry.get('permissions'))
    
    return output

# Returns a dictionary of file name to (id, permissions)
def get_all_entry_permissions(service, parent):
    output = {}

    res = service.files().list(corpora="user",
                               pageSize=1000,
                               fields="files(id, name, permissions)",
                               q=f'"{parent}" in parents',
                               spaces="drive").execute()
    for entry in res.get('files'):
        output[entry.get('name')] = (entry.get('id'), entry.get('permissions'))
    return output

# Examines the permissions list, returning the id if it contains the "anyone" entry
def public_id(permissions_list):
    for permission in permissions_list:
        if permission['type'] == 'anyone':
            return permission['id']
    return None

def should_be_private(name):
    for extension in PRIVATE:
        if name[-len(extension):] == extension:
            return True
    return False

def should_be_public(name):
    for extension in PUBLIC:
        if name[-len(extension):] == extension:
            return True
    return False

# Fixes all the permissions stored in the permissions dictionary
def fix_permissions(service, batch, permissions_dict, allPrivate=False):
    fixed = False

    # Compare the name to the file endings, see if it should be private or public
    for name in permissions_dict:
        shouldBePrivate = allPrivate or should_be_private(name)
        shouldBePublic = name == "Audio" or name == "Parts" or should_be_public(name)
        # for extension in PRIVATE:
        #     if shouldBePrivate: break
        #     shouldBePrivate = name[-len(extension):] == extension
        # for extension in PUBLIC:
        #     if shouldBePublic: break
        #     shouldBePublic = name[-len(extension):] == extension
        

        if not shouldBePublic and not shouldBePrivate: continue
        permission_id = public_id(permissions_dict[name][1])
        if permission_id and shouldBePrivate:
            fixed = True
            print(f'Found item "{name}" that should be private, but is public')
            batch.add(service.permissions().delete(fileId=permissions_dict[name][0], permissionId=permission_id))
        if not permission_id and shouldBePublic:
            fixed = True
            print(f'Found item "{name}" that should be public, but is private')
            batch.add(service.permissions().create(fileId=permissions_dict[name][0],
                                                   body={'type': 'anyone', 'role': 'reader'}))
    return fixed

def batch_callback(request_id, response, exception):
    if exception:
        print("WARNING: Error occurred in batch permissions update:", exception)