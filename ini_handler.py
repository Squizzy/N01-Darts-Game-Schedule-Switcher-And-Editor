from tkinter import messagebox
from pathlib import Path
from os import getenv
from tkinter.filedialog import askopenfilename
import toml # type: ignore

class N01Ini:
    _ini_installer_path: str = ""
    _ini_current_path: str = ""
    _ini_installer_schedule_found:bool = False
    _ini_current_path_schedule_found = False
    
    _filename_for_modified_ini_file_with_path: str
    
    _original_ini_from_toml: dict[str, dict[str, str|int]] = {}
    _original_ini_file_with_path: str = ""

    
    
    _modified_ini_with_imported_schedule: dict[str, dict[str, str|int]] = {}
    _updated_ini_file_with_path: str = ""

    def __init__(self):
        
        if not self.load_original_ini_file():
            # TODO: maybe something to inform the instantiator?
            ...
            
        # print("Loading n01.ini file")
        
        # self._identify_ini_files()
        
        # if not self._select_original_ini_file_path():
        #     messagebox.showerror(title="Error selecting n01.ini file", message="no ini file selected")
        #     return

        # if not self._load_original_ini_file():
        #     messagebox.showerror(title="Error loading n01.ini file", message="Error in loading TOML data")
        #     return
           
        # print("n01.ini file (game settings and schedule if one) loaded successfully")
        # ic(len(self._original_ini_from_toml))

    @property
    def ini_file_location(self) -> str:
        return self._original_ini_file_with_path
    
    @property
    def original_ini_data_from_toml(self) -> dict[str, dict[str, str|int]]:
        return self._original_ini_from_toml
    
    
    def load_original_ini_file(self) -> bool:
        
        def has_schedule(path: Path) -> bool:
            with open(path, "r") as f:
                file=f.readlines()
                found:bool = False
                for line in file:
                    if "[schedule]" in line:
                        found = True
                        break
                return found
                
        def identify_ini_files() -> None:
            
            def file_found_at_path(path: Path) -> tuple[bool, bool]:
                if Path.exists(path):
                    return True, has_schedule(path)
                return False, False
            
            # if N01 installer has been run, the ini file is located in the virtual store

            installer_ini_path: Path = Path(str(getenv("LOCALAPPDATA"))) / "VirtualStore" / "Program Files (x86)" / "n01" / "n01.ini"

            file_found: bool = False
            schedule_found: bool = False
            
            file_found, schedule_found = file_found_at_path(installer_ini_path)
            if file_found:
                self._ini_installer_path = str(installer_ini_path)
                if schedule_found:
                    self._ini_installer_schedule_found = True
                    
                
            # Search in the current path
            current_path = Path(".") / "n01.ini"
            file_found, schedule_found = file_found_at_path(current_path)
            if file_found:
                self._ini_current_path = str(current_path)
                if schedule_found:
                    self._ini_current_path_schedule_found = True
            
        def select_original_ini_file_path() -> bool:
            
            # If there is a usable ini in the installer folder, offer to use it
            if self._ini_installer_path == "":
                messagebox.showinfo(title="game settings with schedule", 
                                    message="No game settings found\nthat includes a schedule\nat installer path location")
                    
            else:
                if self._ini_installer_schedule_found:
                    answer:bool = messagebox.askyesno(title="game settings with schedule found", 
                                                    message="Game settings found\nfrom game installer\nwhich includes a schedule\nUse it?")
                else:
                    answer = messagebox.askyesno(title="game settings with schedule found", 
                                                message="Game settings found\nfrom game installer\nbut does NOT includes a schedule\nUse it (and create and empty schedule)?")
                if answer:
                    self._original_ini_file_with_path = self._ini_installer_path
                    return self._original_ini_file_with_path != ""
            
            # If there is a usable ini in the current path, offer to use it
            if self._ini_current_path == "":
                messagebox.showinfo(title="game settings with schedule", 
                                    message="No game settings found\nthat includes a schedule\nin current directory")        
                
            else:    
                if self._ini_current_path_schedule_found:
                    answer = messagebox.askyesno(title="game settings with schedule found", 
                                                message="Game settings found\nin current path\nwhich includes a schedule\nUse it?")
                else:
                    answer = messagebox.askyesno(title="game settings with schedule found", 
                                                message="Game settings found\nin current path\nbut does NOT includes a schedule\nUse it (and create and empty schedule)?")
                if answer:
                    self._original_ini_file_with_path = self._ini_current_path
                    return self._original_ini_file_with_path != ""
            
            # If above not found or not used, 
            # ask for a file location,  starting from current directory
            title: str = "Select n01.ini file"
            filetypes: list[tuple[str, str]] = [("INI files", "*.ini"), ("TOML files", "*.toml"), ("All files", "*.*")]
            self._original_ini_file_with_path = askopenfilename(title=title, initialdir=".", filetypes=filetypes)
            
            if self._original_ini_file_with_path != "":
                if not has_schedule(Path(self._original_ini_file_with_path)):
                    answer = messagebox.askyesno(title="game settings loaded", 
                                                message="game settings loaded\nbut no schedule in it.\nuse it (and create and empty schedule)?")
                    if not answer:
                        self._original_ini_file_with_path = ""
                
            return self._original_ini_file_with_path != ""

        def load_original_ini_file() -> bool:
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

    
        identify_ini_files()
        
        if not select_original_ini_file_path():
            messagebox.showerror(title="Error selecting n01.ini file", message="no ini file selected")
            return False

        if not load_original_ini_file():
            messagebox.showerror(title="Error loading n01.ini file", message="Error in loading TOML data")
            return False
        return True

    
    def replace_original_schedule_with_imported_schedule(self, imported_schedule: dict[str, str|int]) -> None:
        
        # ic(imported_schedule)
        
        self._modified_ini_with_imported_schedule = self._original_ini_from_toml.copy()
        self._modified_ini_with_imported_schedule["schedule"] = {}
        # self._modified_ini_with_imported_schedule["schedule"]["count"] = len(imported_schedule)
        self._modified_ini_with_imported_schedule["schedule"] = imported_schedule
        
        # for row in modified_ini_with_imported_schedule["schedule"]:
            # pass
        #     ic(row)
            # ic(f"{modified_ini_with_imported_schedule["schedule"][row]}, {self._original_ini_from_toml["schedule"][row]}, {row} ")     
        

    def save_ini_with_updated_schedule(self) -> None:
        
        def select_modified_ini_file_path() -> bool:
                    
            title: str = "Select where to save the updated n01.ini file"
            filetypes: list[tuple[str, str]] = [("INI files", "*.ini"), ("All files", "*.*")]
            initial_dir: str
            
            if self._original_ini_file_with_path != "":
                initial_dir = self._original_ini_file_with_path
            else:
                initial_dir = "."
            
            self._filename_for_modified_ini_file_with_path = askopenfilename(title=title, initialdir=initial_dir, filetypes=filetypes)
                
            return self._filename_for_modified_ini_file_with_path != ""

        def save_ini_file(filename:str, data: dict[str, dict[str, str|int]]) -> bool:
            
            try:
                # turn the dict into a list of strings to be saved
                untomled_list: list[str] = toml.dumps(data).splitlines()
                
                with open(filename, "w") as f:
                    for line in untomled_list:
                        this_line: str = line.strip()
                        
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
        
        select_modified_ini_file_path()
        save_ini_file(self._filename_for_modified_ini_file_with_path, self._modified_ini_with_imported_schedule)
