# standard modules
from tkinter import messagebox
from pathlib import Path
from os import getenv
from tkinter.filedialog import askopenfilename

# pip imported modules
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
        """ Initializes the N01Ini class. Loads the n01.ini file and sets up initial state.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        if not self.load_original_ini_file():
            # TODO: maybe something to inform the instantiator?
            ...

    @property
    def ini_file_location(self) -> str:
        """ Returns the path to the current n01.ini file that has been selected.

        Args:
            None
            
        Returns:
            str: The path to the n01.ini file.
        """
        return self._original_ini_file_with_path
    
    @property
    def original_ini_data_from_toml(self) -> dict[str, dict[str, str|int]]:
        """ Returns the n01.ini data loaded from TOML as a dictionary.

        Args: 
            None

        Returns:
            dict[str, dict[str, str|int]]: The n01.ini data as a TOML dictionary.
        """
        return self._original_ini_from_toml
    
    
    def load_original_ini_file(self) -> bool:
        """ Loads the original n01.ini file and converts it from TOML to a dictionary.

        Args:
            None
            
        Returns:
            bool: True if the file was successfully loaded, False otherwise.
        """        
        
        def has_schedule(path: Path) -> bool:
            """ Checks if the file at the given path contains a "[schedule]" section.

            Args:
                path (Path): The path to the file to check.

            Returns:
                bool: True if the file contains a "[schedule]" section, False otherwise.
            """
            with open(path, "r") as f:
                file=f.readlines()
                for line in file:
                    if "[schedule]" in line:
                        return True
                return False
                
        def identify_ini_files() -> None:
            """ Identifies the location of the n01.ini file based on whether it's in the installer's 
            virtual store or the current directory.

            Args:
                None

            Returns:
                None
            """
            
            def file_found_at_path(path: Path) -> tuple[bool, bool]:
                """ Checks if the file at the given path exists and if it contains a "[schedule]" section.

                Args:
                    path (Path): The path to the file to check.

                Returns:
                    tuple[bool, bool]: A tuple containing:
                        - bool: True if the file exists, False otherwise.
                        - bool: True if the file contains a "[schedule]" section, False otherwise.
                """
                if Path.exists(path):
                    return True, has_schedule(path)
                return False, False
            
            file_found: bool = False
            schedule_found: bool = False 
            
            # if N01 installer has been run, the ini file is located in the virtual store
            installer_ini_path: Path = Path(str(getenv("LOCALAPPDATA"))) / "VirtualStore" / "Program Files (x86)" / "n01" / "n01.ini"
            
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
            title:str = "game settings with schedule"
            message:str
            settings_found:str = "Game settings found"
            location_installer:str = "At the location the installer sets"
            location_current_path:str = "In the current folder"
            location_selected:str = "At the location selected"
            contains_schedule:str = "Includes a schedule"
                
            if self._ini_installer_path == "":
                message=f"{location_installer}:\n{settings_found}: No\n{contains_schedule}: No"
                messagebox.showinfo(title=title, message=message, icon="info")
                    
            else:
                if self._ini_installer_schedule_found:
                    message=f"{location_installer}:\n{settings_found}: Yes\n{contains_schedule}: Yes\nUse it?"
                    answer:bool = messagebox.askyesno(title=title, message=message, icon="question")
                else:
                    message="Game settings found\nat location the installer sets\nbut does NOT include a schedul.e\nUse it (and create and empty schedule)?"
                    message=f"{location_installer}:\n{settings_found}: Yes\n{contains_schedule}: No\nUse it (and create and empty schedule)?"
                    answer = messagebox.askyesno(title=title, message=message, icon="question")
                                                
                if answer:
                    self._original_ini_file_with_path = self._ini_installer_path
                    return self._original_ini_file_with_path != ""
            
            # If nothing was used above, try the current path
            # If there is a usable ini in the current path, offer to use it
            if self._ini_current_path == "":
                message=f"{location_current_path}:\n{settings_found}: No\n{contains_schedule}: No"
                messagebox.showinfo(title=title, message=message, icon="info")
                
            else:    
                if self._ini_current_path_schedule_found:
                    message=f"{location_current_path}:\n{settings_found}: Yes\n{contains_schedule}: Yes\nUse it?"
                    answer = messagebox.askyesno(title=title, message=message, icon="question")
                else:
                    message=f"{location_current_path}:\n{settings_found}: Yes\n{contains_schedule}: No\nUse it (and create and empty schedule)?"
                    answer = messagebox.askyesno(title=title, message=message)
                if answer:
                    self._original_ini_file_with_path = self._ini_current_path
                    return self._original_ini_file_with_path != ""
            
            # If above not found or not used, 
            # ask for a file location,  starting from current directory
            title_ask = "Select n01.ini file"
            filetypes: list[tuple[str, str]] = [("INI files", "*.ini"), ("TOML files", "*.toml"), ("All files", "*.*")]
            self._original_ini_file_with_path = askopenfilename(title=title_ask, initialdir=".", filetypes=filetypes)
            
            if self._original_ini_file_with_path != "":
                if not has_schedule(Path(self._original_ini_file_with_path)):
                    message=f"{location_selected}:\n{settings_found}: Yes\n{contains_schedule}: No\nUse it (and create and empty schedule)?"
                    answer = messagebox.askyesno(title=title, message=message, icon="question")
                    if not answer:
                        self._original_ini_file_with_path = ""
                
            return self._original_ini_file_with_path != ""

        def load_original_ini_file() -> bool:
            """ Loads the original ini file content into self._original_ini_from_toml.
            Adds ||| to replace the empty values which is not compliant to TOML
            
            Args:
                None
                
            Returns:
                None
            """
            raw_data_lines: list[str] = []
            raw_data: str = ""
            
            # Create an empty schedule line dataset
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
            
            # Reset the dictionary holding the data as new data will be loaded to replace the current one
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
                messagebox.showerror(title="Loading n01.ini file", message=f"Error loading the ini file:\n{e}", icon="error")
                return False
            
            if "[schedule]" not in raw_data:
                raw_data += "\n".join(empty_schedule)
            
            # move all the recovered data from the file to the dictionary, but parsed from TOML
            self._original_ini_from_toml = toml.loads(raw_data)

            return True

    
        identify_ini_files()
        
        if not select_original_ini_file_path():
            messagebox.showerror(title="Error selecting n01.ini file", message="no ini file selected", icon="warning")
            return False

        if not load_original_ini_file():
            messagebox.showerror(title="Error loading n01.ini file", message="Error in loading TOML data", icon="warning")
            return False
        return True

    
    def replace_original_schedule_with_imported_schedule(self, imported_schedule: dict[str, str|int]) -> None:
        """ Replaces the current schedule in the n01.ini with a new schedule imported or modified.

        Args:
            imported_schedule (dict[str, str|int]): The new schedule data in TOML dictionary.

        Returns:
            None
        """        
        
        self._modified_ini_with_imported_schedule = self._original_ini_from_toml.copy()
        self._modified_ini_with_imported_schedule["schedule"] = {}
        self._modified_ini_with_imported_schedule["schedule"] = imported_schedule
        
        
    def save_ini_with_updated_schedule(self) -> None:
        """Saves the n01.ini file with an updated schedule.

        Args:
            None

        Returns:
            None
        """
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
                # turn the dict into a list of strings to be saved using the TOML standard
                untomled_list: list[str] = toml.dumps(data).splitlines()
                
                with open(filename, "w") as f:
                    for line in untomled_list:
                        this_line: str = line.strip()
                        
                        # Restore the un-toml no-value where there were none
                        if this_line.endswith('"|||"'):
                            this_line = this_line[:-5]
                            
                        # Remove the spaces that somehow propped up inbetween the = when dumping
                        # Both are toml compliant but this reflects how to original app formatted it
                        if " = " in this_line:
                            this_line = this_line.replace(" = ", "=")
                            
                        f.write(this_line + '\n')
                        
            except Exception as e:
                messagebox.showerror(title="Saving n01.ini file", message=f"Error saving the ini file:\n{e}", icon="error")
                return False
                
            return True
        
        select_modified_ini_file_path()
        save_ini_file(self._filename_for_modified_ini_file_with_path, self._modified_ini_with_imported_schedule)
