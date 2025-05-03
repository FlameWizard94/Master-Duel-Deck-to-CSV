if __name__ == "__main__":
    print(f'\nImporting Reader...\n')

import csv
import easyocr
import cv2
import pyautogui
import numpy as np
import mss
import mss.tools
import time
import warnings
import pyperclip
import keyboard
import time
from tkinter import Tk
import json
import subprocess
import sys
from pathlib import Path 
import threading
from functools import partial
import logging

def update_card_database():
    script_dir = Path(__file__).parent
    
    fetch_script_path = script_dir / "DecorateYDK-main" / "fetch_card_info_json.py"
    output_file = script_dir / "cardinfo.json"
    
    print(f"Downloading card database to {output_file}...\n")
    try:
        cmd = [
            sys.executable,  # Uses the same Python interpreter
            str(fetch_script_path)
        ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                check=True
            )
        print("Card database updated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating card database:\n{e.stderr.decode()}")

    return True

def find_closest_card(start, cardinfo):
    with open(cardinfo, 'r', encoding='utf-8') as f:
        card_db = json.load(f)

    all_card_names = [card['name'] for card in card_db['data']]
    ll_check = ''

    # Simple called by correction, not perfect, use bin tree?
    if 'l' in start:
        for x in range(len(start)):
            if start[x] == 'l':
                ll_check = start[:x] + 'l' + start[x:]
                

    
    for name in all_card_names:
        if name.startswith(start):
            return name
        elif ll_check and name.startswith(ll_check):
            return name

    return None

def DeckName():
    pyautogui.leftClick(641, 134)
    keyboard.press('ctrl')
    keyboard.press('c')
    time.sleep(0.1)  
    keyboard.release('c')
    keyboard.release('ctrl')

    time.sleep(0.2)

    try:
        copied_text = pyperclip.paste()
    except:
        r = Tk()
        r.withdraw()
        try:
            copied_text = r.clipboard_get()
        except:
            copied_text = ""
        finally:
            r.destroy()

    pyautogui.leftClick(741, 164)
    
    #print(f"Deck Name:{copied_text}")
    return copied_text

def RegionMSS(tuple):
    dict = {
        'left': tuple[0],
        'top': tuple[1],
        'height': tuple[2],
        'width': tuple[3]
    }
    return dict

def CardName(reader, decorate_path, cardinfo):
    card_name_region = {
        'left': 635,
        'top': 151,
        'height': 50,
        'width': 1065
    }
    DDD_VARIANTS = {
        'D/DID': 'D/D/D',
        'DID/D': 'D/D/D',
        'D/ DID': 'D/D/D',
        'D /D /D': 'D/D/D',
        'DIDIDID': 'D/D/D/D'
    }

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)

        with mss.mss() as sct:
            screenshot = sct.grab(card_name_region)
            #mss.tools.to_png(screenshot.rgb, screenshot.size, output="card_name.png")
            img = np.array(screenshot)
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((2, 2), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1)  
        processed_img = cv2.bitwise_not(dilated)

        #cv2.imwrite(f"processed.png", processed_img)

        results = reader.readtext(
            processed_img,
            decoder='beamsearch',
            beamWidth=5,
            width_ths=2.5, 
            text_threshold=0.4,
            low_text=0,
            allowlist='''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&<>.,:!%()[]{@}'/#_=+|" -''',  # Added hyphen
            paragraph=False
        )

    if not results:
        return ""
    
    results.sort(key=lambda x: x[0][0][0])
    full_text = ""
    prev_right = 0
    space_threshold = 15 
    
    for i, (bbox, text, _) in enumerate(results):
        current_left = bbox[0][0]    
        if i > 0 and (current_left - prev_right) > space_threshold:
            if text.strip() == '-' or full_text.endswith('-'):
                full_text += text
            else:
                full_text += ' ' + text
        else:
            full_text += text
            
        prev_right = bbox[1][0] 
    
    for variant, correct in DDD_VARIANTS.items():
        full_text = full_text.replace(variant, correct)    
    
    #print(f'{full_text}\n')
    if full_text == 'Caled by the Grave':
        return 'Called by the Grave'
    
    if len(full_text) >= 31 and decorate_path.exists() and cardinfo.exists():
        matched_card = find_closest_card(full_text, cardinfo)
        if matched_card:
            return matched_card
        
    return full_text.strip()
    
def NumCards(reader):
    num_cards_region = {
        'left': 721,
        'top': 177,
        'height': 30,
        'width': 35
    }
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)

        with mss.mss() as sct:
            screenshot = sct.grab(num_cards_region)
            #mss.tools.to_png(screenshot.rgb, screenshot.size, output="num_cards.png")
            img = np.array(screenshot)
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((2, 2), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1) 
        processed_img = cv2.bitwise_not(dilated)

        results = reader.readtext(
            processed_img,
            decoder='beamsearch',
            beamWidth=5,
            width_ths=2.5,  
            text_threshold=0.4,
            low_text=0,
            allowlist='''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&<>.,:!%()[]{@}'/#~_=+|" -''',  # Added hyphen
            paragraph=False
        )

    if not results:
        return ""

    results.sort(key=lambda x: x[0][0][0])

    num_cards = ""
    for (bbox, text, con) in results:
        num_cards += text
         
    
    return int(num_cards.strip())

def NumExtra(reader):
    num_in_extra = {
        'left': 721,
        'top': 748,
        'height': 30,
        'width': 35
    }
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)

        with mss.mss() as sct:
            screenshot = sct.grab(num_in_extra)
            #mss.tools.to_png(screenshot.rgb, screenshot.size, output="num_extra.png")
            img = np.array(screenshot)
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((2, 2), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1) 
        processed_img = cv2.bitwise_not(dilated)

        results = reader.readtext(
            processed_img,
            decoder='beamsearch',
            beamWidth=5,
            width_ths=2.5,  
            text_threshold=0.4,
            low_text=0,
            allowlist='''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&<>.,:!%()[]{@}'/#~_=+|" -''',  # Added hyphen
            paragraph=False
        )

    if not results:
        return ""

    results.sort(key=lambda x: x[0][0][0])

    num_cards = ""
    for (bbox, text, con) in results:
        num_cards += text
         
    
    return int(num_cards.strip())

def TXT(main_deck, extra_deck, name):
    script_dir = Path(__file__).parent
    file_name = script_dir / 'decks' / f'{name}.txt'
    Path(script_dir / 'decks').mkdir(parents=True, exist_ok=True)
    with open(f'{file_name}', "w") as f:
        f.write(f'Main Deck\n')
        for card, num in main_deck.items():
            f.write(f'{num}x {card}\n')

        if extra_deck:
            f.write(f'\nExtra Deck\n')
            for card, num in extra_deck.items():
                f.write(f'{num}x {card}\n')

        f.close()

def CSV(main_deck, extra_deck, name):
    try:
        script_dir = Path(__file__).parent
        csv_name = script_dir / 'decks' / f'{name}.csv'
        Path(script_dir / 'decks').mkdir(parents=True, exist_ok=True)
        with open(f"{csv_name}", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Num Cards", "Handtrap", "Starter", "Extender", "Maxx C Counter", "Normal Summon", "Soft Garnet" "Garnet"])  #Holy shit, Fuck Maxx C
            writer.writerows(main_deck.items())  

            writer.writerow([])
            
            #Table 2: Extra Deck
            if extra_deck:
                writer.writerow(["Extra Deck"]) 
                writer.writerow(["Name", "Num Cards"])  
                writer.writerows(extra_deck.items())  

            f.close()

    except PermissionError:
        print(f"Error: Permission denied when trying to write to {name}.csv")
        print(f"Is the file, {name}.csv, open in another program, like Excel?")
        return False
        
    except Exception as e:
        print(f"Unexpected error saving CSV: {e}")
        return False

class KeyboardWatcher:
    def __init__(self):
        self.stop_event = threading.Event()
        self.listener_thread = None
        
    def _listen(self, callback):
        """Internal thread function"""
        keyboard.wait('enter')  # Blocks until Enter is pressed
        callback()
        
    def start(self, callback):
        """Start watching for Enter key in background"""
        self.listener_thread = threading.Thread(
            target=self._listen,
            args=(callback,),
            daemon=True
        )
        self.listener_thread.start()
    
    def end(self):
        keyboard.unhook_all()
        self.listener_thread.join(timeout=0.1)

def Stop(stop_event):
    print("\nEMERGENCY STOP: Saving partial results...")
    print(f'Program Exiting...')
    stop_event.set()
    sys.exit(0)

def main():
    global stop_event #, lock, condition

    #lock = threading.Lock()
    #condition = threading.Condition(lock) 

    stop_event = threading.Event()

    logs = []

    script_dir = Path(__file__).parent
    cardinfo = script_dir / 'cardinfo.json'
    decorate_path = script_dir / 'DecorateYDK-main'
    update = '2'

    if cardinfo.exists() and decorate_path.exists():
        while update != '1' and update != '0':
            print(f'\nDo you want to update the card database?')
            print(f'Enter 1 for yes, 0 for no\n')
            update = input()
            if update == '1':
                update_card_database()
            elif update == '0':
                print(f'Skipping update.\n')
            else:
                print(f'Please enter valid input.')
    elif decorate_path.exists():
        update_card_database()

    '''text = ''

    while text != '1' and text != '0':
        print(f'\nDo you want a text file describing the deck as well?')
        print(f'Enter 1 for yes, 0 for no\n')
        text = input()
        if text != '1' and text != '0':
            print(f'Please enter valid input.')'''

    watcher = KeyboardWatcher()
    watcher.start(partial(Stop, stop_event))

    print(f'\nPress Enter to stop the script.\n')

    easyocr_logger = logging.getLogger('easyocr')
    easyocr_logger.setLevel(logging.ERROR)
    reader = easyocr.Reader(['en'], gpu=False)

    deck_name = DeckName()
    num_cards = NumCards(reader)
    num_extra = NumExtra(reader)
    logs.append(f'Deck Name: {deck_name}\n')
    logs.append(f'Num cards: {num_cards}\n')
    logs.append(f'Num cards in extra: {num_extra}\n')

    right = 0
    down = 103
    num_in_row = 0 #number of cards in a row

    if num_cards < 51:
        right = 76
        num_in_row = 10

    elif num_cards < 56:
        right = 68
        num_in_row = 11

    else:
        right = 62
        num_in_row = 12

    #Clicks
    deck_name_click = (641, 134)
    card_click = (134, 291)
    deselect = (1858, 68)
    first_card = [544, 264]
    first_extra = [541, 834]
    card_pos = [544, 264] #position of first card

    main_deck = {}
    extra_deck = {}

    x = 0
    card = ''

    try:
        while x < num_cards and not stop_event.is_set():
            for y in range(num_in_row):
                if stop_event.is_set():
                    x += 60
                    y += 60

                pyautogui.click(card_pos)
                pyautogui.click(card_click)
                time.sleep(0.5)
                card = CardName(reader, decorate_path, cardinfo)
                
                pyautogui.click(deselect)
                time.sleep(0.1)

                if card:
                    if card in main_deck.keys():
                        main_deck[card] += 1
                    else:
                        main_deck[card] = 1

                card_pos[0] += right
                x += 1

                if x >= num_cards:
                    break

            card_pos[0] = first_card[0]
            card_pos[1] += down


        card_pos = first_extra
        x = 0
        right = 76

        if num_extra - 10 > 0:
            num_in_row = 10
        else:
            num_in_row = num_extra

    
        while x < num_extra and not stop_event.is_set():
            for y in range(num_in_row):
                if stop_event.is_set():
                    x += 60
                    y += 60

                pyautogui.click(card_pos)
                pyautogui.click(card_click)
                time.sleep(0.5)
                card = CardName(reader, decorate_path, cardinfo)
                pyautogui.click(deselect)
                time.sleep(0.1)

                if card:
                    if card in extra_deck.keys():
                        extra_deck[card] += 1
                    else:
                        extra_deck[card] = 1

                card_pos[0] += right
                x += 1

                if x >= num_extra:
                    break

            card_pos[0] = first_card[0]
            card_pos[1] += down


        if not stop_event.is_set():
            CSV(main_deck, extra_deck, deck_name)
            TXT(main_deck, extra_deck, deck_name)
        else:
            logs.append(f'\nTerminated Early\n')

        logs.append(f'Main Deck:\n{main_deck}\n')
        logs.append(f'Extra Deck\n{extra_deck}')

        with open("MD_to_Excel_logs.txt", "w") as f:
            f.writelines(logs)

        print("Done")

    finally:
        # Cleanup when exiting (normally or via interrupt)
        watcher.end()
    

if __name__ == "__main__":
    main()