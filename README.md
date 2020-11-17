# librarianz-scripts
##### Description
A series of tools to automate the Digital Library for the LSJUMB
##### Authors
Dominic "Frodo" DeMarco and Ben "Caffa" Rocklin
##### Contact
webmaster@lsjumb.com (Webmaster) or demarcod@stanford.edu (Primary Author)
##### Notice
The scripts included in this folder are to be edited and used at your own risk. Before running scripts that can alter the digital library, make sure to create a backup.


# Setup
1. Clone this repository
1. Log in to librarian@lsjumb.com online
1. Follow the instructions [here](https://developers.google.com/drive/api/v3/quickstart/python#step_1_turn_on_the) after clicking the "Enable the Drive API" button.
1. When prompted, download the "credentials.json" file and move it into your working directory (likely called librarianz-scripts).
2. Open a terminal window and navigate to the working directory. If you are on windows, the following steps might work better in WSL or Ubuntu. 
3. Run "pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib" in terminal.
4. Run "python3 login.py" in terminal.
5. Follow the link in the Terminal and authorize the program for the webmaster account.

After you run the login script, you will not need to run it again. If the tokens are somehow invalidated, any script you run will prompt you with a link in the Terminal, which corresponds to step 4.

# Scripts

## Redvest Script
This script will create a folder containing the parts and audio/video files for a set of songs that are to be rehearsed in redvest. This was designed for the virtual format, but may prove useful later on.

### To create Red Vest Folders

1. Edit the redvest.json file to contain the name of the new folder you wish to add along with the list of chartz that will be rehearsed.
2. Run "python3 redvest-creator.py" in the terminal.

#### Notes
1. If you wish to have the new folders appear in a new location, you will need to change the "parent-name" field reflect the name of the directory in which to place the new redvest folder.
2. If you wish to output folders grouped per-instrument, set the "individual-sections" field to "True"

## Seperated Folders Script
This script creates "Separated Section Parts" and "Seperated Sibelius Files" folders that organize all the charts on a per-instrument basis and creates a folder exclusively with Sibeilus files. Only run this script if you have added/removed chartz in the Digital Library, or shifted chartz from current to old (or vice versa). Use the Update Chartz script (which does not yet exist) if you are merely updating existing charts.

### To separate the folders and safely reconstruct the Live Digital Library
1. Make sure that the existing Separated Section Folders are no longer contained in the "[LIVE] DigitalLibrary" directory. You will likely see shortcuts to "Current Chartz" and "Old Chartz" folders within the "LSJUMB Digital    Chartz" folder inside the live directory. These shortcuts will be broken when you run this script, and should be    deleted.
2. Run "python3 separated_folders_creator.py" in the Terminal
3. After checking to ensure all is in order, manually re-add the "Current Charts" and "Old Chartz" folders to the "LSJUMB Digital Chartz" folder within the live directory. This should be the same location as the shortcuts you deleted earlier.

#### Warning
You will need to take the Digital Library offline when running this script. The average runtime is 10-20 mins, so expect 15-25 mins of Digital Library downtime.

#### Note
Configure which sections go to which output folders in parts.json. The format of config.json is a series of key-value pairs in the format OUTPUT_NAME: [INSTRUMENT NAMES]. For instance, the pair CPG: [Clarz, Picz] would send all pieces with "Clarz" or "Picz" in the name to the folder "CPG" (inside the main "Separated Section Parts" output folder). In other words, if you want all songs labelled "SONGNAME - Clarz" and "SONGNAME - Picz" to go to the "CPG" folder, the above example would accomplish this. At present, an example for both the words "Trumpz" and "Trumpets" going to the "Trumpz" output folder is in parts.json.
