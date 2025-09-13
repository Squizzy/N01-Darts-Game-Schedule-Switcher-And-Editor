# from icecream import ic # type: ignore
from datetime import datetime
import csv
import tkinter as tk
from tkinter.filedialog import askopenfilename
from os import path, remove
import shutil
    
def load_current_ini(ini_file: str = "n01.ini") -> dict[str, list[tuple[str, str|None|int]]]:
    parsed_ini: dict[str, list[tuple[str, str|None|int]]]
    
    with open(ini_file, "r") as file:
        data: list[str] = file.readlines()
        
        # extract information into a dictionary by calling the below function
        parsed_ini = parse_ini_file_data_into_dict(data)
        
    return parsed_ini
    # return parsed["schedule"]


def parse_ini_file_data_into_dict(data: list[str]) -> dict[str, list[tuple[str, str|None|int]]]:
    parsed_ini: dict[str, list[tuple[str, str|None|int]]] = {}
    group_tag: str = ""
    item_name:str = ""
    item_value: str|None|int
    
    # take one line at a time. 
    # These will be the lines in the order they are in the ini file
    for line in data:
        # remove extraneous blanks
        line = line.strip()
        
        # if the line starts with [ an ends with ] it is a new group
        if line.startswith("[") and line.endswith("]"):
            group_tag = line # [1:-1] # take the name but remove the [ ] (maybe no?)
            parsed_ini[group_tag] = []
            continue
        # otherwise it is information
        else:
            dict_element = line.split("=", 1) # separate into the key and the value
            item_name = dict_element[0].strip() # remove extraneous blanks possibly
            if len(dict_element) == 2: # if there is a value, get it as a string
                item_value = str(dict_element[1]).strip()
                if item_value.isdigit(): # and if it actually a int, convert it to it
                    item_value = int(item_value)
            else:
                item_value = None

            # add the key pair to the disctionary for the current group
            parsed_ini[group_tag].append((item_name, item_value)) 
    
    return parsed_ini


def extract_current_ini_schedule_from_current_ini(parsed_ini: dict[str, list[tuple[str, str|None|int]]]) -> list[tuple[str, str|None|int]]:
    # simply extracts the schedule information, which is what we are playing with here.
    
    return parsed_ini["[schedule]"]


def sort_current_ini_schedule_info_by_round(current_ini_schedule: list[tuple[str, str|None|int]]) -> dict[int, list[tuple[str, str|int|None]]]:
    sorted_by_round: dict[int, list[tuple[str, str|int|None]]] = {}

    for item_name, item_value in current_ini_schedule:
        # skip empty entries or the count entry as they have not interesting information
        if item_name == "": continue
        if item_name == "count": continue

        # the round value for this item is the decimal value at the end of the key name, 
        # but we don't know if it is 1, 2 or maybe 3 digits (more than 999 rounds sounds rare...)
        # so get the last 3 digits of the name, if they are not a number only take 2 digits and if not only take 1
        round_str = item_name[-3:] if item_name[-3:].isnumeric() else item_name[-2:] if item_name[-2:].isnumeric() else item_name[-1:]
        round = int(round_str)
        
        # if the dictionary key for the round does not already exist, create it with an empty table as value
        if round not in sorted_by_round:
            sorted_by_round[round] = []    
            
        # the add the round data to the round table
        sorted_by_round[round].append((item_name, item_value))
        
    return sorted_by_round


def display_schedule(sorted_by_round: dict[int, list[tuple[str, str|int|None]]]) -> None:
    # display the schedule passed in argument
    # Can be the current ini schedule, or the one that has been loaded
    # attempds to display it in terminal, but it looks ugly,
    # but that's not critical anyway
    
    this_round = ""
    for item in sorted_by_round[0]:
        this_round += f"    {item[0]}"

    if len(this_round) > 100: this_round = this_round[:100] + "..."
    print(f"round\t{this_round}")

    for round in sorted_by_round:
        this_round = ""
        for item in sorted_by_round[round]:
            this_round += f"\t{item[1]}"
        
        if len(this_round) > 100: this_round = this_round[:100] + "..."
        print(f"{round:2}\t{this_round}")


def export_schedule_to_csv(sorted_by_round: dict[int, list[tuple[str, str|int|None]]]) -> None:
    
    # create a subname to make sure existing files are not overwritten
    # and with date in name it is easier to find
    new_file_subname:str = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-"
    filename: str = new_file_subname + "schedule.csv"
    
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        
        # Add headers using the various items names of a round
        headers: list[str] = ["round"]
        for item in sorted_by_round[0]:
            headers.append(item[0])
        writer.writerow(headers)
        
        # Add values using the various item values of each round
        for round in sorted_by_round:
            row: list[str|int|None] = [round]
            for item in sorted_by_round[round]:
                row.append(item[1])
            writer.writerow(row)

    
def import_schedule_from_csv(filename: str) -> dict[int, list[tuple[str, str|int|None]]]:
    
    parsed_imported_schedule: dict[int, list[tuple[str, str|int|None]]] = {}
    
    with open(filename, "r", newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)

        for row in reader:
            round = int(row[headers.index("round")])
           
            for i in range(1, len(headers)):
                # recreate the item name from the header by
                # removing the last digit of the name (it is a "0")
                # then replace this value with the round number
                item_name = headers[i][:-1] + str(round)
                
                # recover the value and save it as a string or a int (or None)
                item_value: str|int|None
                value = row[i]
                if value is None:       item_value = None
                elif value.isalpha():   item_value = str(value)
                elif value.isdigit():   item_value = int(value)
                else:                   item_value = value
                
                # If the round key does not exist, create it
                if round not in parsed_imported_schedule:
                    parsed_imported_schedule[round] = []
                    
                # Store the pair (name/value) into the resulting table for this round    
                parsed_imported_schedule[round].append((item_name, item_value))

    return parsed_imported_schedule


def insert_new_schedule_into_loaded_current_ini(imported_schedule: dict[int, list[tuple[str, str|int|None]]], current_ini: dict[str, list[tuple[str, str|None|int]]]) -> dict[str, list[tuple[str, str|None|int]]]:
    
    updated_ini: dict[str, list[tuple[str, str|None|int]]] = {}
    
    updated_ini = current_ini.copy()
    
    # Erase the current schedule section
    # And save the number of rounds as count value
    updated_ini["[schedule]"] = [("count", len(imported_schedule))]
    
    # Save each round details into the schedule section
    for round in imported_schedule:
        for item in imported_schedule[round]:
            updated_ini["[schedule]"].append(item)
    
    return updated_ini


def save_new_ini_file(new_ini: dict[str, list[tuple[str, str|None|int]]], file_to_import: str = "") -> None:

    filebase: str = path.basename(file_to_import).split('.')[0]
    savepath: str = path.dirname(file_to_import)

    # the output will be to a new name filename every time
    # to avoid overwrites risk
    # date/time is used to find easily
    new_file_subname:str = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-"
    save_filename = path.join(savepath, new_file_subname + filebase + '-' + "n01.ini")
    
    space_needed = False
    with open(save_filename, "w") as f:
        
        for group in new_ini:
            
            # Save the group name (space with one line if not the first entry)
            if space_needed: f.write('\n')
            space_needed = True
            f.write(group + '\n')  
            
            # Save the group data
            for data in new_ini[group]:
                if data[0] == "": continue
                if data[1] == "": f.write(f"{data[0]}=\n")
                else: f.write(f"{data[0]}={data[1]}\n")

    print(f"ini file {save_filename} saved successfully. You can now rename it to your preferred name")


def select_file(title:str, filetypes: list) -> str:
    root=tk.Tk()
    root.withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(title=title, initialdir=".", filetypes=filetypes) # show an "Open" dialog box and return the path to the selected file
    print(filename)
    return filename


def switch_ini_files() -> bool:

    # Select the ini file to use
    title = "Select schedule file to use:"
    filetypes=[("INI files", "*.ini")]
    ini_file = select_file(title=title, filetypes=filetypes)
    if ini_file == "":
        print("No file selected, exiting")
        return False
    
    ini_path: str = path.dirname(ini_file)
    original_ini_file: str = path.join(ini_path, "n01.ini")
    original_ini_backup: str = path.join(ini_path, "backup_original_n01.ini")
    
    # first, if there is no backup of the ini file, make one
    if not path.exists(original_ini_backup):
        if path.exists(original_ini_file):
            shutil.copy2(original_ini_file, original_ini_backup)

    # remove the current ini file
    if path.exists(original_ini_file): 
        remove(original_ini_file)
    
    # replace by the selected ini file
    shutil.copy2(ini_file, original_ini_file)
    
    return True



# Macros for the main application, using the above functions
def load_specific_schedule_into_game() -> None:
    
    print("Please close the app if running")
    input("Press enter when closed")
    
    if not switch_ini_files():
        print("Problem switching files, aborting")
        return
    
    print("""
        The new schedule has been loaded successfully")
        In order to use it:
         - In game: start a new game (Game > New Game... > OK)
         - Then load the schedule (Game > New Schedule > Game On)""")
    

def export_current_ini_schedule_to_csv(ini_file: str = "n01.ini") -> None:
    
    # Select the file to import
    title = "Select ini file to import and extract the schedule into CSV:"
    filetypes=[("INI files", "*.ini")]
    ini_file = select_file(title=title, filetypes=filetypes)
    if ini_file == "":
        print("No file selected, exiting")
        return
    
    current_ini: dict[str, list[tuple[str, str|None|int]]] = load_current_ini(ini_file)
    current_ini_schedule: list[tuple[str, str|None|int]] = extract_current_ini_schedule_from_current_ini(current_ini)
    current_ini_schedule_sorted_by_round: dict[int, list[tuple[str, str|int|None]]] = sort_current_ini_schedule_info_by_round(current_ini_schedule)
    # display_schedule(current_ini_schedule_sorted_by_round)
    export_schedule_to_csv(current_ini_schedule_sorted_by_round)
    
    
def load_new_schedule_from_csv_and_export_to_ini_file(ini_file: str = "n01.ini") -> None:
    
    # Select the file to import
    title="Select schedule CSV to create a new ini file with"
    filetypes=[("CSV files", "*.csv")]
    file_to_import = select_file(title=title, filetypes=filetypes)
    if file_to_import == "":
        print("No file selected, exiting")
        return
    
    # load the current ini file    
    current_ini: dict[str, list[tuple[str, str|None|int]]] = load_current_ini(ini_file)

    # load the schedule from the csv file
    imported_schedule: dict[int, list[tuple[str, str|int|None]]] = import_schedule_from_csv(file_to_import)
    
    # display_schedule(new_schedule)
    
    # insert the new schedule into the current ini file
    new_ini: dict[str, list[tuple[str, str|None|int]]] = insert_new_schedule_into_loaded_current_ini(imported_schedule, current_ini)
    
    # save the new ini file
    save_new_ini_file(new_ini, file_to_import)


def main() -> int:
    
    print(""" Schedule Switcher for N01 Darts Game Scores Keeper
    Schedule switcher for n01 darts score keeper, Windows version
    V0.1.0
    options:
    1) Select a game schedule and start the game with it (closes the deletes open game and )
    2) Extract (to CSV) the exist schedule from the game's initialisation file
    3) Load a new schedule from a CSV file into the game's initialisation file
    0) exit
    
    NOTE: A CSV file can be imported into Excel, Libreoffice etc to be modified, 
          but must be saved in the same format
    """)
    key = ""
    while True:
        key = input("Enter your choice: ")
        if key == '1':
            load_specific_schedule_into_game()
            break
        if key == '2':
            export_current_ini_schedule_to_csv()
            break
        if key == '3':
            load_new_schedule_from_csv_and_export_to_ini_file()
            break
        if key == '0':
            print("key 0 pressed, exiting")
            break
        else:
            print("Invalid choice, please try again.")
    
    
    # # ini file to load from - default is this, when this app is run from the same folder
    # ini_file:str = "n01.ini"
    
    # # This does what the below does, but in one command
    # # export_current_ini_schedule_to_csv(ini_file) 
    
    # current_ini: dict[str, list[tuple[str, str|None|int]]] = load_current_ini(ini_file)
    # current_ini_schedule: list[tuple[str, str|None|int]] = extract_current_ini_schedule_from_current_ini(current_ini)
    # current_ini_schedule_sorted_by_round: dict[int, list[tuple[str, str|int|None]]] = sort_current_ini_schedule_info_by_round(current_ini_schedule)
    # # display_schedule(current_ini_schedule_sorted_by_round)
    # # export_schedule_to_csv(current_ini_schedule_sorted_by_round)
    
    # # name of the file to import
    # file_to_import: str = "schedule1.csv"
    
    # imported_schedule: dict[int, list[tuple[str, str|int|None]]] = import_schedule_from_csv(file_to_import)
    # # display_schedule(new_schedule)
    # new_ini: dict[str, list[tuple[str, str|None|int]]] = insert_new_schedule_into_loaded_current_ini(imported_schedule, current_ini)
    # save_new_ini_file(new_ini)
    
    
    # print("Option:")
    # print("1: display current schedule")
    # print("2: export schedule to CSV to open in Excel/Google Sheet/Libreoffice/etc")
    # print("3: import schedule from CSV and replace current schedule")
    
    return 0


if __name__ in "__main__":
    main()