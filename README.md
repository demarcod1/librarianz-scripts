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
2. Open a terminal window and navigate to the working directory.
3. Run `pip3 install -r requirements.txt` in terminal (or `py -m pip install -r requirements.txt` if on Windows).
4. Run `python3 librarianz_scripts.py -s login` in terminal (or `py .\librarianz_scripts.py -s login` if on Windows).
5. Follow the link in the Terminal and authorize the program for the webmaster account.

After you run the login script, you will not need to run it again. If the tokens are somehow invalidated, any script you run will prompt you with a link in the Terminal, which corresponds to the final step.

</details>

# Using the GUI
Run `python3 librarianz_scripts.py` (or `py .\librarianz_scripts.py` on Windows) to open the GUI, where you can access the scripts and configure the options without having to manually edit any `.json` files.

# Scripts
Click on the `Show/Hide Details` tabs for detailed information and notes about each script and documentation of their configuration `.json` files.

## Folder Creator Script
This script generates pdf folders for the specified parts

<details>
   <summary>Show/Hide Details</summary>
   
### To genereate folders

1. Edit the `scripts/options/folder_creator_options.json` file. More details about this file can be found [here](#understanding-folder_creator_optionsjson)
2. Run `python3 librarianz_script -s folder_creator` in the terminal

#### Notes

1. It is required that you have already downloaded the parts files from the Digital Library before running this script by using the [Download Parts Script](#download-parts-script). It is recommended to download somewhat frequently to ensure your local machine's files are up-to-date
2. The `"folder-dir"` option must be the same for when you downloaded the files and when you wish to create the folders
3. For more detailed output, set the `"verbose"` option to `true`
4. Some error-checking will happen when you run this script, but it is recommended to run the [Validate Folder Files Script](#validate-folder-files-script) with `"verbose": true` to double-check your file spellings and generate a sample table of contents page
   
</details>

## Upload Files Script
This script intelligently uploads files from a specified location on your machine into the Digital Library system.

<details>
   <summary>Show/Hide Details</summary>

### To upload files to the Digital Library

1. Edit the `scripts/options/upload_options.json` file as needed
2. Run `python3 librarianz_script -s upload_files` in the terminal

#### Configuring `upload_options.json`
* `mode` can be one of the following:
    * 0 - update existing files (but do not add new ones)
    * 1 - add new files (but do not update existing ones)
    * 2 - update and add files
* `new-charts` is an array of `{ "name": string, "to": number }` entries, specifying the name of a new chart and whether it should be placed in the current or old chartz category (0 = current, 1 = old)
* `require-titles-match` controls whether, when updating part files, the titles must exactly match or can differ in the alias used to refer to a certain part. For example, if you wish to update the file `Chart Name - toobz.pdf` with the file `Chart Name - tööbz.pdf`, you will need to change this option to false
* `resources-directory` is a file path to the directory that contains the files you wish to add/update. This script will not recursively check subdirectories, so all files that are intended to be added must live directly in this directory
* `supported-file-types` is a list of file extensions that can be added to the Digital Library

#### Notes
1. Shortcuts for parts and sibelius files will automatically be generated. If the Digital Library is already live, it will update in real-time without any further action
2. If the script is telling you that a file or folder already exists, but you can't see it on the web, then check the trash
3. In order for part files to be recognized, the must be named `{chartname} - {partname}.pdf` (for example, `All Right Now - Bonz.pdf`). The chartnames must match for all files.

</details>

## Download Parts Script
This script downloads the part files form the Digital Library and stores them on your local machine to be read by the folder creator script

<details>
   <summary>Show/Hide Details</summary>
   
### To download the part files

1. Edit the `scripts/options/folder_creator_options.json` file to specify the destination of the downloaded items and the parts to download.
2. Run `python3 librarianz_script -s download_parts`

#### Configuring `folder_creator_options.json`
This config file has a large number of options, which are fully detailed [here](#understanding-folder_creator_optionsjson). However, you only need to worry about 2 options for the downloading step:

1. `"download-parts"` is an array of part names to download
2. `"folder-dir"` is the directory where the parts will be downloaded

#### Notes

1. If the path in `"folder-dir"` does not already exist, it will be created. If it does exist, any files with the same name will be overwritten
   
</details>

## Move Chartz Script
This script moves chartz to/from the Current Chartz, Old Chartz, and Archive directories

<details>
   <summary>Show/Hide Details</summary>
      

### To move a chart to a different location

1. Edit the `scripts/options/move_chartz_options.json` file to specify which chartz you wish to move, and where you wish to move them
2. Run `python3 librarianz_script -s move_chartz` in the terminal

#### Configuring `move_chartz_options.json`

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
This script creates a folder containing the parts and audio/video files for a set of songs that are to be rehearsed in redvest. This was designed for the virtual format, but may prove useful later on.

<details>
   <summary>Show/Hide Details</summary>

### To create Red Vest Folders

1. Edit the redvest.json file to contain the name of the new folder you wish to add along with the list of chartz that will be rehearsed.
2. Run `python3 librarianz_script -s redvest_creator` in the terminal.

#### Notes
1. If you wish to have the new folders appear in a new location, you will need to change the `parent-name` field reflect the name of the directory in which to place the new redvest folder.
2. If you wish to output folders grouped per-instrument, set the `individual-sections` field to `True`

</details>

## Validate Folder Files Script
This script performs error-checking on your config file for the [Folder Creator Script](#folder-creator-script) and optionally output a sample table of contents page

<details>
   <summary>Show/Hide Details</summary>
   
### To validate the files for the folder creator

1. Edit the `scripts/options/folder_creator_options.json` file to specify the destination of folder files and whether or not to generate table of contents files.
2. Run `python3 librarianz_script -s validate_folder_files`

#### Configuring `folder_creator_options.json`
This config file has a large number of options, which are fully detailed [here](#understanding-folder_creator_optionsjson). However, you only need to worry about 2 options for the downloading step:

1. `"generate-on-validation"` is `true` if you wish to generate a sample of the table of contents, `false` otherwise
2. `"folder-dir"` is the directory where the parts will be downloaded
   
</details>

## Seperated Folders Script
This script has been disabled and will not execute.

This script (re)creates `Separated Section Parts` and `Seperated Sibelius Files` folders that organize all the charts on a per-instrument basis and creates a folder exclusively with Sibeilus files. Only run this script if you wish to completely remake the Digital Library. Other scripts, such as `upload_files` and `move_chartz` will automatically update the live Digital Library.

<details>
   <summary>Show/Hide Details</summary>

### To separate the folders and safely reconstruct the Live Digital Library
1. Make sure that the existing Separated Section Folders are no longer contained in the `[LIVE] DigitalLibrary` directory. You will likely see shortcuts to `Current Chartz` and `Old Chartz` folders within the `LSJUMB Digital Chartz` folder inside the live directory. These shortcuts will be broken when you run this script, and should be deleted.
2. Run `python3 librarianz_script -s separated_folders_creator` in the Terminal
3. After checking to ensure all is in order, manually re-add the `Current Charts` and `Old Chartz` folders to the `LSJUMB Digital Chartz` folder within the live directory. This should be the same location as the shortcuts you deleted earlier.

#### Warning
You will need to take the Digital Library offline when running this script. The average runtime is 10-20 mins, so expect 15-25 mins of Digital Library downtime.

#### Note
Configure which sections go to which output folders in `scripts/options/parts.json`. The format of this file is a series of key-value pairs in the format `OUTPUT_NAME: [INSTRUMENT NAMES]`. For instance, the pair `"CPG": ["Clarz", "Picz"]` would send all pieces with `"Clarz"` or `"Picz"` in the name to the folder `"CPG"` (inside the main `Separated Section Parts` output folder). In other words, if you want all songs labelled `SONGNAME - Clarz` and `SONGNAME - Picz` to go to the `CPG` folder, the above example would accomplish this.

</details>

# Understanding `folder_creator_options.json`
This configuration file for the folder creator is relatively complex. The fields and their meanings are detailed here

<details>
   <summary>Show/Hide Details</summary>

* `"dollie-songs"` - An array of song names that have Dollie dances. These songs will appear in boldface in the Table of Contents
* `"download-parts"`- An array of part names that should be downloaded from the Digital Library
* `"enforce-order"` - An array of orders that must be followed, where each order is an array of song names that must appear one-after-the-other
   * For example, if the song `Foreplay` must be followed by `Knights of Cydonia`, then you will need to add the following rule: `"enforce-order": [ [ "Foreplay", "Knights of Cydonia" ] ]`
* `"enumerate-pages"` - `true` if you wish to add letters/numbers to the chartz, `false` otherwise. For troubleshooting, setting this to `false` make the generation take significantly less time, but remember to set this back to `true` before generating the production folder
* `"fingering-chart"`
   * `"include"` - `true` if you wish to include the fingering chart in the folder, `false` otherwise
   * `"titles"` - An array of names of files that contain the fingering chart data
* `"folder-dir"` - The path to the directory where the folder files will be downloaded to/read from
* `"folder-name"` - The name of the folder - is part of the filename
* `"folder-parts"` - An array of part names for which a folder will be generated
* `"lettered-chartz"` - An array of chart names that should be enumerated with a letter, not a number (such as `All Right Now`)
* `"page-size"` - The dimensions of the page. You probably don't want to change this unless you're changing the page dimensions of all our music
* `"page-num-font"`
   * `"name"` - The name of the font you wish to use for the page numbers. By default, only a small selection of fonts are supported
   * `"size"` - The size of the font you wish to use for the page numbers
* `"teazers"`
   * `"include"` - `true` if you wish to include the teazers in the folder, `false` otherwise
   * `"titles"` - An array of chart names that are teazers
* `"toc"`
   * `"entry"`
      * `"font-normal"` - The font to use in the table of contents for a normal entry (not a dollie song)
      * `"font-dollie"` - The font to use in the table of contents for a dollie song
      * `"size"` - The size of the font - can be adjusted to ensure toc remains on one page
   * `"generate-on-validation"` - `true` if you wish to generate table of contents pages when running the validation script, `false` otherwise. This is useful for ensuring the formatting is how you desire before generating the entire folder
   * `"title"`
      * `"label"` - The title of the table of contents page
      * `"font"` - The font to use for the title
      * `"size"` - The font size to use for the title
   * `"footer"`
      * `"label"` - The text at the bottom of the table of contents page
      * `"font"` - The font to use for the footer
      * `"size"` - The font size to use for the footer
   * `"num-cols"` - The number of columns in the table of contents
* `"verbose"` - `true` if you wish for a more detailed output, `false` otherwise

</details>
