# MD to CSV 

This is a script that looks at a deck in Master Duel and creates a .csv describing it.<br>
I personally use it to manage decks in MS Excel. <br>
The script will control your mouse and keyboard (You press **Enter** to stop the script).<br>
The script will get the deck name.
Then it will look at the amount of cards in the Main and Extra Deck. <br>
Afterwards, the script looks at each card name, one by one, and counts how many of each card is in the deck.

This script can also make use of the Decorate YDK script: https://github.com/HannesHaglund/DecorateYDK <br>

It's used to get card names with over 31 letters.<br>
To use Decorate YDK with my script, just put my script and the the extracted **"DecorateYDK-main"** folder (The folder must be that exact name)
in the same folder. <br>
I recommend getting Decorate YDK, not only for my script, but for managing ydk files.

## Notes
- Press **Enter** to stop the script.
- The script only works if Master Duel is **fullscreen** in your **primary monitor**.
- I tested this with a 1080p monitor. Other types of monitors may not work.
- There may be misspelling, <br>


## Prerequisites
1. Have Python 3 downloaded : https://www.python.org/downloads/

## Installation
1. Download the zip in releases
1. Extract the folder wherever you want
1. Right click the extracted folder and select "open in terminal"
1. Run this command "pip install -r requirements.txt" 

## Usage
1. Have the deck opened like this on your **primary monitor**:

![deck_example](deck_example.png)

2. Run the Python script "md_to_csv.py"

3. The .csv file will appear in a folder called **"decks"** where the script is.

### With Decorate YDK
1. You will be asked to Update the database (Unless a file **"cardinfo.json"** is in the same location as the script).<br>
  cardinfo.json is used for spell checking and getting names longer than 31 characters. <br>
  Update only when new cards are relesed in Yu-Gi-Oh.
  
1. Enter 1 to update the database. This triggers the Decorate YDK script and makes or updates cardinfo.json. <br>
	Enter 0 to skip the update. 

<br>

The script is done when it stops moving your mouse. <br>
**Press Enter to end the script early.** <br>
In an emergency, try to push the mouse to any corner of the screen.
This will cause an error, ending the script.
