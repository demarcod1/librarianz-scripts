import util.util as util
import os, sys

# Lists the files that will be attempted to be updated
def get_files_to_update(options):
    dir = options["update-directory"]
    file_types = options["supported-file-types"]

    print("Verifying update directory...")
    try:
        to_update = [ file for file in os.listdir(dir) if file[-4:] in file_types ]
        if len(to_update) == 0: raise Exception
        return to_update
    except:
        print(f'ERROR: No supported files found in directory "{options["update-directory"]}"')
        sys.exit()

# Retrieves the updatable files for a chart
def get_chart_files(service, library_ids, chart, cache, options):
    if chart in cache : return cache[chart]

    chart_id = util.get_chart_id(service, chart, library_ids)
    if not chart_id: return None
    parts_id = util.get_parts_folder(service, chart, chart_id)
    if not parts_id: return None
    
    cache[chart] = util.get_file_types(service, chart_id, options["supported-file-types"])
    cache[chart].extend(util.get_file_types(service, parts_id, options["supported-file-types"]))
    return cache[chart]
        

# Update the file with the specified path
def attempt_update(service, library_ids, directory, filename, alias_map, cache, options):
    # parse file
    chart, part, mimeType = util.parse_file(filename, alias_map)
    files = get_chart_files(service, library_ids, chart, cache, options)

    if not files: return

    for file in files:
        # if part field is non-null, make sure part aliases match up
        if file.get("name") == filename or (part and util.parse_file(file.get("name"), alias_map)[1] == part):
            if(util.update_file(service, file.get("id"), f'{directory}{filename}', new_mime_type=mimeType)):
                print(f'Successfully updated "{filename}"')
                return
    print(f'WARNING: Could not update file "{filename}"')

def main():
    # Parse parts options
    alias_map = util.make_alias_map(util.parse_options("parts.json"))

    # Parse options and files
    options = util.parse_options("update_library_options.json")
    to_update = get_files_to_update(options)

    # Build service, get digital library
    print("Verifying DigitalLibrary format...")
    service = util.build_service()
    _, curr_id, old_id = util.get_digital_library(service)

    # Update each file, keep track of know folder locations
    cache = {}
    for filename in to_update:
        attempt_update(service, [curr_id, old_id], options["update-directory"], filename, alias_map, cache, options)

if __name__ == '__main__':
    main()
