from googleapiclient.errors import HttpError
from scripts.util.thread_events import check_stop_script
import scripts.util.util as util


def clear_broken_shortcuts():
    # Build drive
    service = util.build_service()
    check_stop_script()

    # Verify all needed folders exist and retrieve their ids
    print("Verifying DigitalLibrary format...")
    lib_ids = util.get_digital_library(service)
    library_id = lib_ids.get("library_id")
    if library_id == None: return 1

    sep_ids = util.get_separated_folders(service, library_id)
    if sep_ids == None: return 1

    sep_parts = {
        age: { folder["name"]: folder["id"] for folder in util.get_drive_files(service, sep_ids[f"sec_{age}"], files_only=False) }
            for age in ["curr", "old", "future"]
    }
    sep_audio = {
        age: { folder["name"]: folder["id"] for folder in util.get_drive_files(service, sep_ids[f"aud_{age}"], files_only=False) }
            for age in ["curr", "old", "future"]
    }
    print("Examining shortcuts...")

    allFolders = []
    for age in ["curr", "old", "future"]:
        allFolders.extend(sep_parts[age].values())
        allFolders.extend(sep_audio[age].values())
        allFolders.append(sep_ids[f"sib_{age}"])

    for id in allFolders:
        for file in util.get_drive_files(service, id, is_shortcut=True):
            targetId = file.get("shortcutDetails").get("targetId")
            try:
                targetFile = service.files().get(fileId=targetId, fields="trashed").execute()
                if targetFile["trashed"] is True:
                    raise Exception
            except:
                print(f'File pointed to by {file.get("name")} is a broken shortcut.')
                service.files().delete(fileId=file.get("id")).execute()

    return 0