# librarianz-scripts
##### Description
A series of tools to automate the Digital Library for the LSJUMB
##### Author
Dominic "Frodo" DeMarco
##### Contact
webmaster@lsjumb.com (Webmaster) or demarcod@stanford.edu (Primary Author)
##### Notice
The scripts included in this folder are to be edited and used at your own risk. Before running scripts that can alter the digital library, make sure to create a backup.


# Setup

<details>
   <summary>Click to show setup steps</summary>

### Setup steps

1. Clone this repository
1. Log in to librarian@lsjumb.com online
1. Follow the instructions [here](https://developers.google.com/drive/api/v3/quickstart/python#step_1_turn_on_the) after clicking the "Enable the Drive API" button.
1. When prompted, download the "credentials.json" file and move it into your working directory (likely called librarianz-scripts).
2. Open a terminal window and navigate to the working directory. If you are on windows, the following steps might work better in WSL or Ubuntu. 
3. Run `pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib` in terminal.
4. Run `python3 login.py` in terminal.
5. Follow the link in the Terminal and authorize the program for the webmaster account.

After you run the login script, you will not need to run it again. If the tokens are somehow invalidated, any script you run will prompt you with a link in the Terminal, which corresponds to the final step.

</details>

# Scripts

## Upload Files Script
This script will intelligently upload files from a specified location on your machine into the Digital Library system.

<details>
   <summary>Show/Hide Details</summary>

### To upload files to the Digital Library

1. Edit the `options/upload_options.json` file as needed
2. Run `python3 upload_files.py` in the terminal

#### Configuring upload_options.json
* `mode` can be one of the following:
    * 0 - update existing files (but do not add new ones)
    * 1 - add new files (but do not update existing ones)
    * 2 - update and add files
* `new-charts` is an array of `{ "is-current" : bool, "name": string }` entries, specifying the name of a new chart and whether it should be placed in the current or old chartz category
* `require-titles-match` controls whether, when updating part files, the titles must exactly match or can differ in the alias used to refer to a certain part. For example, if you wish to update the file `Chart Name - toobz.pdf` with the file `Chart Name - tööbz.pdf`, you will need to change this option to false
* `resources-directory` is a file path to the directory that contains the files you wish to add/update. This script will not recursively check subdirectories, so all files that are intended to be added must live directly in this directory
* `supported-file-types` is a list of file extensions that can be added to the Digital Library

#### Notes
1. Shortcuts for parts and sibelius files will automatically be generated. If the Digital Library is already live, it will update in real-time without any further action
2. If the script is telling you that a file or folder already exists, but you can't see it on the web, then check the trash

</details>

## Move Chartz Script
This script will move charts to/from the Current Chartz, Old Chartz, and Archive directories

<details>
   <summary>Show/Hide Details</summary>
      

### To move a chart to a different location

1. Edit the `options/move_chartz_options.json` file to specify which chartz you wish to move, and where you wish to move them
2. Run `python3 move_chartz.py` in the terminal

#### Configuring move_chartz_options.json

* `chartz` is an array of chartz that you wish to move. Each element `{ "name": string, "to": number }` contains:
   * `name` - the name of the chart
   * `to` - the location where this chart should be moved. This value is a number from 0 to 2:
      * 0 - Move to `Current Chartz`
      * 1 - Move to `Old Chartz`
      * 2 - Archive this chart (move it to `Digital LibraryArchives/Chart Data` directory

#### Notes
1. This script will automatically update all shortcuts and references in the Separated Sibelius Files/Section Parts directories
   1. If the chart is being moved to the archive, a new subdirectory called `Shortcuts` will be created to store the shortcuts
   2. If the chart is being moved from the archive back into the main library, the shortcuts will be re-added, and the `Shortcuts` folder will be removed
2. Once a chart has been moved to the archive, it can be found in the `Archive/Chart Data` directory. From there, it can be safely manipulated or deleted without affecting the live DigitalLibrary

</details>

## Redvest Script
This script will create a folder containing the parts and audio/video files for a set of songs that are to be rehearsed in redvest. This was designed for the virtual format, but may prove useful later on.

<details>
   <summary>Show/Hide Details</summary>

### To create Red Vest Folders

1. Edit the redvest.json file to contain the name of the new folder you wish to add along with the list of chartz that will be rehearsed.
2. Run `python3 redvest_creator.py` in the terminal.

#### Notes
1. If you wish to have the new folders appear in a new location, you will need to change the `parent-name` field reflect the name of the directory in which to place the new redvest folder.
2. If you wish to output folders grouped per-instrument, set the `individual-sections` field to `True`

</details>

## Seperated Folders Script
This script creates `Separated Section Parts` and `Seperated Sibelius Files` folders that organize all the charts on a per-instrument basis and creates a folder exclusively with Sibeilus files. Only run this script if you have added/removed chartz in the Digital Library, or shifted chartz from current to old (or vice versa). Use the Update Chartz script (which does not yet exist) if you are merely updating existing charts.

<details>
   <summary>Show/Hide Details</summary>

### To separate the folders and safely reconstruct the Live Digital Library
1. Make sure that the existing Separated Section Folders are no longer contained in the `[LIVE] DigitalLibrary` directory. You will likely see shortcuts to `Current Chartz` and `Old Chartz` folders within the `LSJUMB Digital Chartz` folder inside the live directory. These shortcuts will be broken when you run this script, and should be deleted.
2. Run `python3 separated_folders_creator.py` in the Terminal
3. After checking to ensure all is in order, manually re-add the `Current Charts` and `Old Chartz` folders to the `LSJUMB Digital Chartz` folder within the live directory. This should be the same location as the shortcuts you deleted earlier.

#### Warning
You will need to take the Digital Library offline when running this script. The average runtime is 10-20 mins, so expect 15-25 mins of Digital Library downtime.

#### Note
Configure which sections go to which output folders in `options\parts.json`. The format of this file is a series of key-value pairs in the format `OUTPUT_NAME: [INSTRUMENT NAMES]`. For instance, the pair `"CPG": ["Clarz", "Picz"]` would send all pieces with `"Clarz"` or `"Picz"` in the name to the folder `"CPG"` (inside the main `Separated Section Parts` output folder). In other words, if you want all songs labelled `SONGNAME - Clarz` and `SONGNAME - Picz` to go to the `CPG` folder, the above example would accomplish this.

</details>
