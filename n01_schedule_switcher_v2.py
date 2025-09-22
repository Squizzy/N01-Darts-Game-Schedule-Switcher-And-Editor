import toml # type: ignore
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import csv
# from typing import Any
import tkinter as tk # type: ignore
from tkinter import ttk # type: ignore
import os
from tktooltip import ToolTip # type: ignore 
#from typing import Any

from icecream import ic # type: ignore

class N01Ini:
    _ini_installer_path: str = ""
    _ini_current_path: str = ""
    _ini_installer_schedule_found:bool = False
    _ini_current_path_schedule_found = False
    
    _original_ini_from_toml: dict[str, dict[str, str|int]] = {}
    _original_ini_file_with_path: str = ""
    
    _modified_ini_with_imported_schedule: dict[str, dict[str, str|int]] = {}
    _updated_ini_file_with_path: str = ""

    def __init__(self):
        # print("Loading n01.ini file")
        
        self._identify_ini_files()
        
        if not self._select_original_ini_file_path():
            messagebox.showerror(title="Error selecting n01.ini file", message="no ini file selected")
            return

        if not self._load_original_ini_file():
            messagebox.showerror(title="Error loading n01.ini file", message="Error in loading TOML data")
            return
           
        # print("n01.ini file (game settings and schedule if one) loaded successfully")
        # ic(len(self._original_ini_from_toml))

    @property
    def ini_file_location(self) -> str:
        return self._original_ini_file_with_path
    
    @property
    def original_ini_data_from_toml(self) -> dict[str, dict[str, str|int]]:
        return self._original_ini_from_toml
    
    def _has_schedule(self, path) -> bool:
        with open(path, "r") as f:
            file=f.readlines()
            found:bool = False
            for line in file:
                if "[schedule]" in line:
                    found = True
                    break
            return found
        
    def _file_found_at_path(self, path) -> tuple[bool, bool]:
        if os.path.exists(path):
            return True, self._has_schedule(path)
        return False, False
            
    def _identify_ini_files(self) -> None:
            
        # if N01 installer has been run, the ini file is located in the virtual store
        # %appdata%/Local/virtualStore/Programs Files (x86)/n01
        installer_ini_path:str = os.path.join(str(os.getenv("LOCALAPPDATA")), "virtualStore", "Programs Files (x86)", "n01", "n01.ini")
        file_found: bool = False
        schedule_found: bool = False
        
        file_found, schedule_found = self._file_found_at_path(installer_ini_path)
        if file_found:
            self._ini_installer_path = installer_ini_path
            if schedule_found:
                self._ini_installer_schedule_found = True
                
            
        # Search in the current path
        current_path:str =os.path.join(".", "n01.ini")
        file_found, schedule_found = self._file_found_at_path(current_path)
        if self._file_found_at_path(current_path):
            self._ini_current_path = current_path
            if schedule_found:
                self._ini_current_path_schedule_found = True
        
    def _select_original_ini_file_path(self) -> bool:
        
        # If there is a usable ini in the installer folder, offer to use it
        if self._ini_installer_path != "":
            if self._ini_installer_schedule_found:
                answer:bool = messagebox.askyesno(title="game settings with schedule found", 
                                                  message="Game settings found\nthat includes a schedule\nfrom game installer\nUse it?")
            else:
                answer = messagebox.askyesno(title="game settings with schedule found", 
                                             message="Game settings found\nbut does NOT includes a schedule\nfrom game installer\nUse it (and create and empty schedule)?")
            if answer:
                self._original_ini_file_with_path = self._ini_installer_path
                return self._original_ini_file_with_path != ""
        else:
            messagebox.showinfo(title="game settings with schedule", 
                                message="No game settings found\nthat includes a schedule\nat installer path location")
        
        # If there is a usable ini in the current path, offer to use it
        if self._ini_current_path != "":
            if self._ini_current_path_schedule_found:
                answer = messagebox.askyesno(title="game settings with schedule found", 
                                             message="Game settings found\nthat includes a schedule\nin current path\nUse it?")
            else:
                answer = messagebox.askyesno(title="game settings with schedule found", 
                                             message="Game settings found\nbut does NOT includes a schedule\nin current path\nUse it (and create and empty schedule)?")
            if answer:
                self._original_ini_file_with_path = self._ini_current_path
                return self._original_ini_file_with_path != ""
        else:
            messagebox.showinfo(title="game settings with schedule", 
                                message="No game settings found\nthat includes a schedule\nin current directory")        
        
        # If above not found or not used, 
        # ask for a file location,  starting from current directory
        title: str = "Select n01.ini file"
        filetypes: list[tuple[str, str]] = [("INI files", "*.ini"), ("TOML files", "*.toml"), ("All files", "*.*")]
        self._original_ini_file_with_path = askopenfilename(title=title, initialdir=".", filetypes=filetypes)
        
        if not self._has_schedule(self._original_ini_file_with_path):
            answer = messagebox.askyesno(title="game settings loaded", 
                                         message="game settings loaded\nbut no schedule in it.\nuse it (and create and empty schedule)?")
            if not answer:
                self._original_ini_file_with_path = ""
               
        return self._original_ini_file_with_path != ""

    def _load_original_ini_file(self) -> bool:
        raw_data_lines: list[str] = []
        raw_data: str = ""
        
        empty_schedule = [
            "[schedule]\n",
            "count=0",
            "start_score_0=0\n",
            "round_limit_0=0\n",
            "round_0=0",
            "max_leg_0=0\n",
            "best_of_0=0\n",
            "change_first_0=0\n",
            'p1_name_0="player1"\n',
            "p1_start_score_0=0\n",
            "p1_com_0=0\n",
            "p1_com_level_0=0\n",
            'p2_name_0="player2"\n',
            "p2_start_score_0=0\n",
            "p2_com_0=0\n",
            "p2_com_level_0=0\n"
            ]
        
        self._original_ini_from_toml = {}
        
        try:
            with open(self._original_ini_file_with_path, "r") as f:
                raw_data_lines=f.readlines()
                
                lines_count = len(raw_data_lines)
                for this_line in range(lines_count):
                    line = raw_data_lines[this_line].strip()
                    
                    # make the line where there is no value for the key toml compliant 
                    # by adding some chars unlikely to be used
                    raw_data += line + ('"|||"\n' if line.endswith('=') else "\n")

        except ValueError as e:
            messagebox.showerror(title="Error loading n01.ini file", message=f"error: {e}")
            return False
        
        if "[schedule]" not in raw_data:
            raw_data += "\n".join(empty_schedule)
        
        self._original_ini_from_toml=toml.loads(raw_data)

        return True
    
    def replace_original_schedule_with_imported_schedule(self, imported_schedule: dict[str, str|int]) -> None:
        
        # ic(imported_schedule)
        
        self._modified_ini_with_imported_schedule = self._original_ini_from_toml.copy()
        
        self._modified_ini_with_imported_schedule["schedule"]["count"] = len(imported_schedule)
        self._modified_ini_with_imported_schedule["schedule"] = imported_schedule
        
        # for row in modified_ini_with_imported_schedule["schedule"]:
            # pass
        #     ic(row)
            # ic(f"{modified_ini_with_imported_schedule["schedule"][row]}, {self._original_ini_from_toml["schedule"][row]}, {row} ")     
        
    def _select_modified_ini_file_path(self) -> bool:
                
        title: str = "Select where to save the updated n01.ini file"
        filetypes: list[tuple[str, str]] = [("INI files", "*.ini"), ("All files", "*.*")]
        
        if self._original_ini_file_with_path != "":
            initial_dir = self._original_ini_file_with_path
        else:
            initial_dir = "."
        
        self._modified_ini_file_with_path = askopenfilename(title=title, initialdir=initial_dir, filetypes=filetypes)
               
        return self._modified_ini_file_with_path != ""

    def _save_ini_file(self, filename:str, data: dict[str, dict[str, str|int]]) -> bool:
        
        try:
            # turn the dict into a list of strings to be saved
            untomled_list: list[str] = toml.dumps(data).splitlines()
            
            with open(filename, "w") as f:
                for line in untomled_list:
                    this_line = line.strip()
                    
                    # Restore the un-toml no-value where there were none
                    if this_line.endswith('"|||"'):
                        this_line = this_line[:-5]
                        
                    # Remove the spaces that somehow propped up inbetween the = when dumping
                    # This is still toml compliant but it is not clear if the app would work with the spaces in
                    if " = " in this_line:
                        this_line = this_line.replace(" = ", "=")
                        
                    f.write(this_line + '\n')
                    
        except Exception as e:
            messagebox.showerror(title="Error saving n01.ini file", message=f"error: {e}")
            return False
            
        return True

    def save_ini_with_updated_schedule(self) -> None:
        
        self._select_modified_ini_file_path()
        self._save_ini_file(self._modified_ini_file_with_path, self._modified_ini_with_imported_schedule)
        

class Schedule:
    _original_schedule: dict[str, str|int] = {}
    _original_schedule_sorted_by_set: dict[int, dict[str, str|int]] = {}
    
    _schedule_csv_to_import: str = ""
    _imported_schedule: dict[str, str|int] = {}
    _imported_schedule_sorted_by_set: dict[int, dict[str, str|int]] = {}
    
    _schedule_header: list[str] = []
    
    schedule_headers = {
            "start_score": "Round level (eg 301, 501, 701, ...)",
            "round_limit": "option to stop the round after this limit hs been played",
            "round": "Number of rounds",
            "max_leg": "Number of legs for the set",
            "best_of": "Stop this set once this number of legs has been won by a player",
            "change_first": "If enabled, alternate the starter from the previous round",
            "p1_name": "Name of the player or team",
            "p1_start_score": "Start score of player with handicap (eg handicap 10 for a 301 -> 291)",
            "p1_com": "If enabled, computer player",
            "p1_com_level": "Player difficulty level for computer player (if enabled)",
            "p2_name": "Name of the player or team",
            "p2_start_score": "Start score of player with handicap (eg handicap 10 for a 301 -> 291)",
            "p2_com": "If enabled, computer player",
            "p2_com_level": "Player difficulty level for computer player (if enabled)",
    }
    
    def __init__(self):
        pass
        
    @property
    def original_schedule(self) -> dict[str, str|int]:
        return self._original_schedule
    
    @property
    def original_schedule_sorted_by_set(self) -> dict[int, dict[str, str|int]]:
        return self._original_schedule_sorted_by_set
    
    @property
    def imported_schedule(self) -> dict[str, str|int]:
        return self._imported_schedule
    
    def extract_schedule_from_original_ini(self, data) -> bool:

        if "schedule" not in data:
            messagebox.showerror(title="Error in loading n01.ini file", message="The schedule section is missing in the n01.ini file.")
            return False

        self._original_schedule = data["schedule"]
        self._sort_schedule_from_toml_by_set(self._original_schedule)
        return True

    def _sort_schedule_from_toml_by_set(self, data: dict[str, str|int]) -> None:
        # Group the data into rounds
        self._original_schedule_sorted_by_set = {}
        
        for key in data:
            this_set: int = 0
            
            if key == "count":
                continue
            
            this_set = int(key[-3:]) if key[-3:].isnumeric() else int(key[-2:]) if key[-2:].isnumeric() else int(key[-1])

            if this_set not in self._original_schedule_sorted_by_set:
                self._original_schedule_sorted_by_set[this_set] = {}
                
            self._original_schedule_sorted_by_set[this_set][key[:-(len(str(this_set)) + 1)]] = data[key]

    def _extract_schedule_headers(self) -> None:

        for key in self._original_schedule_sorted_by_set[0]:
            self._schedule_header.append(key[:-2])
    
    def save_schedule_as_csv(self, data: dict[str, str|int], filename) -> bool:
        
        # turn the dict into a list of strings to be saved
        untomled_list: list[str] = toml.dumps(data).splitlines()
        
        # remove the stubs for the entries without values
        untomled_list = list(map(lambda line: line[:-5] if line.endswith('"|||"') else line, untomled_list))

        # Extract the headers
        self._sort_schedule_from_toml_by_set(data)
        self._extract_schedule_headers()

        # Save the CSV data
        try:        
            with open(filename, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self._schedule_header)
                writer.writeheader()
                
                for set in range(len(self._original_schedule_sorted_by_set)):
                    this_row_data: dict[str, str|int] = {}
                    for key in self._schedule_header:
                        # The headers do not that the "_0" or "_1" etc 
                        # so this need to be indicated when writing the CSV to ensure it goes to the correct column
                        this_row_data[key] =  self._original_schedule_sorted_by_set[set][f"{key}_{set}"]
                    writer.writerow(this_row_data)

        except Exception as e:
            messagebox.showerror(title="Error saving schedule csv file", message=f"error: {e}")
            return False
                    
        return True
    
    def _get_csv_file_path(self) -> bool:
        
        title: str = "Select the schedule file to import"
        filetypes: list[tuple[str, str]] = [("CSV files", "*.csv"), ("All files", "*.*")]
        self._schedule_csv_to_import = askopenfilename(title=title, initialdir=".", filetypes=filetypes)
               
        return self._schedule_csv_to_import != ""
    
    def _load_schedule_from_csv(self) -> bool:
        
        if not self._get_csv_file_path():
            return False
        
        try:
            with open(self._schedule_csv_to_import, "r") as f:
                reader = csv.DictReader(f)
                
                row: dict[str, str|int]
                set = 0
                for row in reader:
                    this_set = row
                
                    # create the round key
                    if set not in self._imported_schedule_sorted_by_set:
                        self._imported_schedule_sorted_by_set[set] = {}
                
                    # import the values as int or str as needed
                    for key in this_set:
                        if str(this_set[key]).isnumeric():
                            self._imported_schedule_sorted_by_set[set][key] = int(this_set[key])
                        else:
                            if '"' in str(row[key]):
                                row[key] = str(row[key]).replace('"', '')
                                
                            self._imported_schedule_sorted_by_set[set][f"{key}"] = row[key]
                    
                    set += 1
            
        except FileNotFoundError as e:
            messagebox.showerror(title="CSV file to import", message=f"file {self._schedule_csv_to_import} not found:\n{e}")
            return False
        
        return True

    def import_schedule_from_csv(self) -> bool:
        if not self._load_schedule_from_csv():
            return False

        if not self._convert_imported_schedule_to_toml_schedule():
            return False
        
        return True
    
    def _convert_imported_schedule_to_toml_schedule(self) -> bool:
        # Convert the imported schedule to a toml string
        
        for set in self._imported_schedule_sorted_by_set:
            for key in self._imported_schedule_sorted_by_set[set]:
                self._imported_schedule[f"{key}_{set}"] = self._imported_schedule_sorted_by_set[set][key]
                
        return True


class UI:
    _window:tk.Tk
    _buttons_frame:tk.Frame
    _schedule_frame:tk.Frame
    _modify_padx:int
    _modify_pady:int
    _style:ttk.Style
    
    _original_schedule:dict[int, dict[str, str|int]] = {}
    _original_schedule_loaded:bool = False 
    
    _modified_schedule:dict[int, dict[str, str|int]] = {}
    
    
    def __init__(self):
        # initialise Tk window
        self._window = tk.Tk()
        
        # display the window
        self._window.title("N01 Schedule Switcher")
        self._window.configure(background="DarKGreen")
        self._window.minsize(800,600)
        self._window.maxsize(1920,1080)
        self._window.config(width=800, height=600)    
        
        self._buttons_frame = tk.Frame(self._window, bg="yellow", width=790)
        self._schedule_frame = tk.Frame(self._window, bg="lightblue")
    
        self._generate_buttons_frame()    
        
    def _generate_buttons_frame(self) -> None:

        # Generate a frame for the buttons
        # self._buttons_frame = tk.Frame(self._window, bg="yellow")
        self._buttons_frame.place(x = 10, y = 10)
        
        buttons_width:int = 30
        self._style = ttk.Style()
        
        self._style.configure("quit.TButton", background="red", justify=tk.CENTER, anchor=tk.CENTER, bordercolor="gray")
        # - Load schedule from ini
        load_original_schedule = ttk.Button(self._buttons_frame, text="Load current game schedule", command=self._load_original_ini_schedule, width=buttons_width)
        # - Display original schedule
        display_original_schedule = ttk.Button(self._buttons_frame, text="Display current game current schedule", command=self._display_original_schedule, width=buttons_width)
        # - Load schedule from csv
        load_schedule_from_csv = ttk.Button(self._buttons_frame, text="Load schedule from csv", command=self._load_modified_schedule, width=buttons_width)
        # - Display loaded schedule
        display_modified_schedule = ttk.Button(self._buttons_frame, text="Display loaded/modified schedule", command=self._display_modified_schedule, width=buttons_width)
        # - Modify schedule
        modify_schedule = ttk.Button(self._buttons_frame, text="Modify loaded schedule", command=self._modify_schedule, width=buttons_width)
        # - Save schedule
        save_schedule = ttk.Button(self._buttons_frame, text="Save loaded/modified schedule", command=self._save_schedule, width=buttons_width)
        # - Set modified schedule to game
        set_schedule = ttk.Button(self._buttons_frame, text="Set modified schedule to game", command=self._set_schedule, width=buttons_width)
        # - quit
        quit_app = ttk.Button(self._buttons_frame, text="Quit", command=self._quit, width=buttons_width-10, style="quit.TButton")

        # Add the buttons to the frame
        load_original_schedule.grid(    row=0, column=0, columnspan=1, padx=5, pady=2)
        display_original_schedule.grid( row=1, column=0, columnspan=1, padx=5, pady=2)
        
        load_schedule_from_csv.grid(    row=0, column=1, columnspan=1, padx=5, pady=2)
        display_modified_schedule.grid( row=1, column=1, columnspan=1, padx=5, pady=2)
        modify_schedule.grid(           row=2, column=1, columnspan=1, padx=5, pady=2)
        save_schedule.grid(             row=3, column=1, columnspan=1, padx=5, pady=2)
        set_schedule.grid(              row=3, column=0, columnspan=1, padx=5, pady=2)
        
        quit_app.grid(                  row=1, column=3, columnspan=1, padx=5, pady=2)
   
    def _load_original_ini_schedule(self) -> None:
        
        ini_file:N01Ini = N01Ini()
        ini_schedule:Schedule = Schedule()

        self._original_schedule = {}

        if not(ini_schedule.extract_schedule_from_original_ini(ini_file.original_ini_data_from_toml)):
            return

        self._original_schedule = ini_schedule.original_schedule_sorted_by_set
        
        # ic(ini_file.original_ini_data_from_toml)
        # ic(ini_schedule.original_schedule_sorted_by_set)
        # ic(self._original_schedule)
        
        if self._original_schedule is not None:
            self._original_schedule_loaded = True
            
        self._display_original_schedule()

    def _load_modified_schedule(self) -> None:
        schedule: Schedule = Schedule()
        
        schedule.import_schedule_from_csv()
        self._modified_schedule= schedule._imported_schedule_sorted_by_set
        
        self._display_modified_schedule()
 
    def _display_original_schedule(self) -> None:
        self._display_schedule(self._original_schedule)

    def _display_modified_schedule(self) -> None:
        self._display_schedule(self._modified_schedule)
        
    def _display_schedule(self, schedule:dict[int, dict[str, str|int]] = {}) -> None:
        
        if schedule is None:
            messagebox.showinfo("request schedule not loaded")
            return

        if self._schedule_frame is not None:
            self._schedule_frame.grid_forget()
            self._schedule_frame.destroy()
            
        # Non-scrollable frame
        self._schedule_frame = tk.Frame(self._window, bg="lightblue")
        self._schedule_frame.place(x = 10, y = 140)
        
        # Non-working scrollable frame as per: https://blog.teclado.com/tkinter-scrollable-frames/
        # schedule_frame:tk.Frame = tk.Frame(self._window, bg="lightblue")
        # canvas = tk.Canvas(schedule_frame)
        # scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=canvas.yview)
        # original_schedule_frame = ttk.Frame(canvas)
        # original_schedule_frame.bind(
        #     "<Configure>",
        #     lambda e: canvas.configure(
        #         scrollregion=canvas.bbox("all")
        #     )
        # )        
        # canvas.create_window((10, 80), window=original_schedule_frame, anchor="nw")
        # canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pre-define the widths of the table cells
        # Note that this this does not adapt if font is face or size is changed
        columns_width = {
            "start_score": 6,
            "round_limit": 6,
            "round": 6,
            "max_leg": 4,
            "best_of": 4,
            "change_first": 7,
            "p1_name": 10,
            "p1_start_score": 6,
            "p1_com": 5,
            "p1_com_level": 5,
            "p2_name": 10,
            "p2_start_score": 6,
            "p2_com": 5,
            "p2_com_level": 5,
        }
        
        # Define the style for the headers and for the values
        # self._style = ttk.Style()
        

        # Generate a table of textboxes to display the original schedule
        x = 0
        y = 0
        
        # Create a label for each header in the schedule
        self._style.configure("header.TLabel", 
                background="lightblue", 
                )       
        
        header = ttk.Label(self._schedule_frame, 
                    text="set\nno", 
                    width=3,
                    justify=tk.CENTER,  
                    anchor=tk.CENTER,   
                    foreground="red",
                    style="header.TLabel"
                    )
        header.grid(row=y, column=x, padx=1, pady=1)
        x += 1

        for key, _ in schedule[0].items():
            header = ttk.Label(self._schedule_frame, 
                               text=str(key).replace("_", "\n"), 
                               width=columns_width[key],
                               justify=tk.CENTER,  
                               anchor=tk.CENTER,
                               style="header.TLabel"
                               )
            header.grid(row=y, column=x, padx=1, pady=1)
            x += 1
        y += 1
        x = 0
        
        # Create a textbox for each value in the schedule
        self._style.configure("value.TLabel",
                background="white", 
                )
        
        for row_key in schedule:
            textbox = ttk.Label(self._schedule_frame, 
                    text=str(y), 
                    width=3, 
                    foreground = "red",
                    anchor=tk.CENTER,
                    style="value.TLabel"
                    )
            textbox.grid(row=y, column=x, padx=1, pady=1)
            x += 1
            
            for col_key in schedule[row_key]:
                
                if col_key in ["change_first", "p1_com", "p2_com", "round_limit", "best_of"]:
                    text_value = "✓" if schedule[row_key][col_key] == 1 else "✕"
                else:
                    text_value = str(schedule[row_key][col_key])
                    
                textbox = ttk.Label(self._schedule_frame, 
                                    text=text_value, 
                                    width=columns_width[col_key], 
                                    anchor=tk.CENTER,
                                    style="value.TLabel"
                                    )
                textbox.grid(row=y, column=x, padx=1, pady=1)
                x += 1
            y += 1
            x = 0
            
            # header = ttk.Label(original_schedule_frame, text=str(key).replace("_", "\n"), justify=tk.CENTER, background="lightblue")
                # textbox = ttk.Entry(original_schedule_frame)
                # textbox.insert(0, str(self._original_schedule[row_key][col_key]))
    
    def _modify_schedule(self) -> None:
        self._modify_loaded_schedule(self._modified_schedule)
        
    def _modify_loaded_schedule(self, schedule:dict[int, dict[str, str|int]]) -> None:
        
        if schedule is None:
            messagebox.showinfo("request schedule not loaded")
            return

        if self._schedule_frame is not None:
            self._schedule_frame.grid_forget()
            self._schedule_frame.destroy()
            
        # Non-scrollable frame
        self._schedule_frame = tk.Frame(self._window, bg="lightblue")
        self._schedule_frame.place(x = 10, y = 170)
        
        # Non-working scrollable frame as per: https://blog.teclado.com/tkinter-scrollable-frames/
        # schedule_frame:tk.Frame = tk.Frame(self._window, bg="lightblue")
        # canvas = tk.Canvas(schedule_frame)
        # scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=canvas.yview)
        # original_schedule_frame = ttk.Frame(canvas)
        # original_schedule_frame.bind(
        #     "<Configure>",
        #     lambda e: canvas.configure(
        #         scrollregion=canvas.bbox("all")
        #     )
        # )        
        # canvas.create_window((10, 80), window=original_schedule_frame, anchor="nw")
        # canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pre-define the widths of the table cells
        # Note that this this does not adapt if font is face or size is changed
        columns_width = {
            "start_score": 6,
            "round_limit": 6,
            "round": 6,
            "max_leg": 4,
            "best_of": 4,
            "change_first": 7,
            "p1_name": 10,
            "p1_start_score": 6,
            "p1_com": 5,
            "p1_com_level": 5,
            "p2_name": 10,
            "p2_start_score": 6,
            "p2_com": 5,
            "p2_com_level": 5,
        }
        
        com_level_values:list[str] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        
        
        # Define the style for the headers and for the values
        # style:ttk.Style = ttk.Style()
        self._style.configure("Custom.TCheckbutton", background="lightblue")
        
        # Set the table variables
        self._start_score_spinbox: dict[int, ttk.Spinbox] = {}
        self._start_score_spinbox_var: dict[int, tk.IntVar] = {}
        self._round_limit_checkbutton: dict[int, ttk.Checkbutton] = {}
        self._round_limit_checkbutton_var: dict[int, tk.BooleanVar] = {}
        self._round_spinbox: dict[int, ttk.Spinbox] = {}
        self._round_spinbox_var: dict[int, tk.IntVar] = {}
        self._max_leg_spinbox: dict[int, ttk.Spinbox] = {}
        self._max_leg_spinbox_var: dict[int, tk.IntVar] = {}
        self._best_of_checkbutton: dict[int, ttk.Checkbutton] = {}
        self._best_of_checkbutton_var: dict[int, tk.BooleanVar] = {}
        self._change_first_checkbutton: dict[int, ttk.Checkbutton] = {}
        self._change_first_checkbutton_var: dict[int, tk.BooleanVar] = {}
        self._p1_name_entry: dict[int, ttk.Entry] = {}
        self._p1_name_entry_var: dict[int, tk.StringVar] = {}
        self._p1_start_score_spinbox: dict[int, ttk.Spinbox] = {}
        self._p1_start_score_spinbox_var: dict[int, tk.IntVar] = {}
        self._p1_com_checkbutton: dict[int, ttk.Checkbutton] = {}
        self._p1_com_checkbutton_var: dict[int, tk.BooleanVar] = {}
        self._p1_com_level_spinbox: dict[int, ttk.Spinbox] = {}
        self._p1_com_level_spinbox_var: dict[int, tk.IntVar] = {}
        self._p2_name_entry: dict[int, ttk.Entry] = {}
        self._p2_name_entry_var: dict[int, tk.StringVar] = {}
        self._p2_start_score_spinbox: dict[int, ttk.Spinbox] = {}
        self._p2_start_score_spinbox_var: dict[int, tk.StringVar] = {}
        self._p2_com_checkbutton: dict[int, ttk.Checkbutton] = {}
        self._p2_com_checkbutton_var: dict[int, tk.BooleanVar] = {}
        self._p2_com_level_combobox: dict[int, ttk.Combobox] = {}
        self._p2_com_level_combobox_var: dict[int, tk.IntVar] = {}
        self._header: dict[int, ttk.Label] = {}
        
        self._modify_padx:int = 2
        self._modify_pady:int = 2
        
        # Generate a table of textboxes to display the original schedule
        x = 0
        y = 0
        
        # Create a label for each header in the schedule
        self._style.configure("header.TLabel", 
                background="lightblue", 
                )       
        
        # Add a column header for a value that does not exist in the schedule
        self._header[x] = ttk.Label(self._schedule_frame, 
                    text="set\nno", 
                    width=3,
                    justify=tk.CENTER,  
                    anchor=tk.CENTER,   
                    foreground="red",
                    style="header.TLabel"
                    )
        self._header[x].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
        x += 1

        # Add the headers
        for key, _ in schedule[0].items():
            self._header[x] = ttk.Label(self._schedule_frame, 
                               text=str(key).replace("_", "\n"), 
                               width=columns_width[key],
                               justify=tk.CENTER,  
                               anchor=tk.CENTER,
                               style="header.TLabel"
                               )
            self._header[x].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
            x += 1
        y += 1
        
        # Add tooltips on the headers
        for i in range(x):
            ToolTip(self._header[i], msg=Schedule.schedule_headers[(self._header[i]["text"]).replace("\n", "_")] if (self._header[i]["text"]).replace("\n", "_") in Schedule.schedule_headers else "n/a")
        
        x = 0
        
        
        for row_key in schedule:
            # Add the set value (information not in the schedule)
            textbox = tk.Label(self._schedule_frame, 
                    text=str(y), 
                    width=3, 
                    foreground="red",
                    anchor=tk.CENTER,
                    # style="value.TLabel"
                    background="lightblue"
                    )
            textbox.grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
            x += 1
            
            # Fill in the data
            for col_key in schedule[row_key]:
                if col_key == "start_score":
                    self._start_score_spinbox_var[row_key] = tk.IntVar()
                    self._start_score_spinbox_var[row_key].set(int(schedule[row_key][col_key]))
                    self._start_score_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
                                                              textvariable=self._start_score_spinbox_var[row_key], from_=1, to=1001, increment=2)
                    self._start_score_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                    
                if col_key == "round_limit":
                    self._round_limit_checkbutton_var[row_key] = tk.BooleanVar()
                    self._round_limit_checkbutton_var[row_key].set(bool(int(schedule[row_key][col_key])))
                    self._round_limit_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, style="Custom.TCheckbutton", width=1,
                                                                      variable=self._round_limit_checkbutton_var[row_key], onvalue=True, offvalue=False)

                    self._round_limit_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)
                    
                if col_key == "round":
                    self._round_spinbox_var[row_key] = tk.IntVar()
                    self._round_spinbox_var[row_key].set(int(schedule[row_key][col_key]))
                    self._round_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
                                                        textvariable=self._round_spinbox_var[row_key], from_=1, to=100, increment=1)
                    self._round_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                    
                if col_key == "max_leg":
                    self._max_leg_spinbox_var[row_key] = tk.IntVar()
                    self._max_leg_spinbox_var[row_key].set(int(schedule[row_key][col_key]))
                    self._max_leg_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
                                                          textvariable=self._max_leg_spinbox_var[row_key], from_=1, to=100, increment=1)
                    self._max_leg_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                    
                if col_key == "best_of":
                    self._best_of_checkbutton_var[row_key] = tk.BooleanVar()
                    self._best_of_checkbutton_var[row_key].set(bool(int(schedule[row_key][col_key])))
                    self._best_of_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, style="Custom.TCheckbutton", width=1,
                                                                  variable=self._best_of_checkbutton_var[row_key], onvalue=True, offvalue=False)
                    self._best_of_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)
                    
                if col_key == "change_first":
                    self._change_first_checkbutton_var[row_key] = tk.BooleanVar()
                    self._change_first_checkbutton_var[row_key].set(bool(int(schedule[row_key][col_key])))
                    self._change_first_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, style="Custom.TCheckbutton", width=1,
                                                                       variable=self._change_first_checkbutton_var[row_key], onvalue=True, offvalue=False)
                    self._change_first_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)
                    
                if col_key == "p1_name":
                    self._p1_name_entry_var[row_key] = tk.StringVar()
                    self._p1_name_entry_var[row_key].set(str(schedule[row_key][col_key]))
                    self._p1_name_entry[row_key] = ttk.Entry(self._schedule_frame, width=columns_width[col_key], 
                                                      textvariable=self._p1_name_entry_var[row_key])
                    self._p1_name_entry[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)

                if col_key == "p1_start_score":
                    self._p1_start_score_spinbox_var[row_key] = tk.IntVar()
                    self._p1_start_score_spinbox_var[row_key].set(int(schedule[row_key][col_key]))
                    self._p1_start_score_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
                                                   textvariable=self._p1_start_score_spinbox_var[row_key], from_=1, to=1001, increment=2)
                    self._p1_start_score_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)

                if col_key == "p1_com":
                    self._p1_com_checkbutton_var[row_key] = tk.BooleanVar()
                    self._p1_com_checkbutton_var[row_key].set(bool(int(schedule[row_key][col_key])))
                    self._p1_com_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame,  style="Custom.TCheckbutton",
                                                           variable=self._p1_com_checkbutton_var[row_key], onvalue=True, offvalue=False)
                    self._p1_com_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)                    

                if col_key == "p1_com_level":
                    self._p1_com_level_spinbox_var[row_key] = tk.IntVar()
                    self._p1_com_level_spinbox_var[row_key].set(int(schedule[row_key][col_key]))
                    self._p1_com_level_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
                                     textvariable=self._p1_com_level_spinbox_var[row_key], from_=1, to=12, increment=1)
                    self._p1_com_level_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                    
                if col_key == "p2_name":
                    self._p2_name_entry_var[row_key] = tk.StringVar()
                    self._p2_name_entry_var[row_key].set(str(schedule[row_key][col_key]))
                    self._p2_name_entry[row_key] = ttk.Entry(self._schedule_frame, width=columns_width[col_key], 
                                                      textvariable=self._p2_name_entry_var[row_key])
                    self._p2_name_entry[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)

                if col_key == "p2_start_score":
                    self._p2_start_score_spinbox_var[row_key] = tk.StringVar()
                    self._p2_start_score_spinbox_var[row_key].set(str(schedule[row_key][col_key]))
                    self._p2_start_score_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
                                                   textvariable=self._p2_start_score_spinbox_var[row_key], from_=1, to=1001, increment=2)
                    self._p2_start_score_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)

                if col_key == "p2_com":
                    self._p2_com_checkbutton_var[row_key] = tk.BooleanVar()
                    self._p2_com_checkbutton_var[row_key].set(bool(int(schedule[row_key][col_key])))
                    self._p2_com_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, style="Custom.TCheckbutton",
                                                           variable=self._p2_com_checkbutton_var[row_key], onvalue=True, offvalue=False)
                    self._p2_com_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)                    

                if col_key == "p2_com_level":
                    self._p2_com_level_combobox_var[row_key] = tk.IntVar()
                    self._p2_com_level_combobox_var[row_key].set(0 if int(schedule[row_key]["p2_com"]) == 0 else int(schedule[row_key][col_key]))
                    self._p2_com_level_combobox[row_key] = ttk.Combobox(self._schedule_frame, width=columns_width[col_key],
                                                                  values=com_level_values, textvariable=self._p2_com_level_combobox_var[row_key])
                    self._p2_com_level_combobox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                                        
                x += 1
            y += 1
            x = 0
    
    def _save_schedule(self) -> None:
        pass

    def _set_schedule(self) -> None:
        pass
    
    def _quit(self)-> None:
        self._window.destroy()
    
    @property
    def start(self) -> None:
        self._window.mainloop()


def main() -> int:
    # ini_file: N01Ini = N01Ini()
    
    # schedule: Schedule = Schedule(ini_file.original_schedule)
    # ic(schedule.original_schedule)
    
    # schedule.save_schedule_as_csv(schedule.original_schedule, "sample_schedule.csv")
    
    # schedule: Schedule = Schedule()
    # schedule.import_schedule_from_csv()
    
    # ini_file.replace_original_schedule_with_imported_schedule(schedule.imported_schedule)
    
    # ini_file.save_ini_with_updated_schedule()
    
    app:UI = UI()
    app.start
    
    return 0


if __name__ in "__main__":
    main()