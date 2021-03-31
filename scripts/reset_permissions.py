from time import sleep
from scripts.util.permissions_utils import batch_callback, fix_permissions, get_all_chart_permissions, get_all_entry_permissions, get_file_permissions
from scripts.util.thread_events import check_stop_script
import scripts.util.util as util
import scripts.util.remake_utils as rm

# Resets and remakes all the permissions 
def reset_permissions():
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

    print("Reading chart permissions...")
    all_chart_permissions = get_all_chart_permissions(service, lib_ids.get("current_id"), lib_ids.get("past_id"), lib_ids.get("future_id"))
    all_chart_batch = service.new_batch_http_request(callback=batch_callback)
    print(len(all_chart_permissions.keys()))
    fixed = fix_permissions(service, all_chart_batch, all_chart_permissions, allPrivate=True)
    if fixed:
        print("Making all chart folders private...")
        all_chart_batch.execute()


    for chartName in all_chart_permissions:
        entry_batch = service.new_batch_http_request(callback=batch_callback)
        chartId = all_chart_permissions[chartName][0]

        # Edit this line if you need to reset the permissions for a single chart
        # if chartName != 'Example Chart': continue
        print(f'Resetting permissions for "{chartName}"')
        entry_permissions = get_all_entry_permissions(service, chartId)
        parts_id, audio_id = util.get_parts_and_audio_folders(service, chartName, chartId)
        entry_permissions.update(get_all_entry_permissions(service, parts_id))
        entry_permissions.update(get_all_entry_permissions(service, audio_id))
        fixed = fix_permissions(service, entry_batch, entry_permissions)
        if fixed:
            print(f'Executing permissions updates')
            sleep(2) # Avoid too many api calls
            entry_batch.execute()
    
    print("Successfully reset permissions")
    
    # check_stop_script()
    # print(f'Executing permissions updates')
    # entry_batch.execute()


    # res = service.files().get(fileId=sep_ids['sib'], fields="permissions").execute()
    # print(res)