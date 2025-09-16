import toml # type: ignore
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import csv
# from typing import Any

from icecream import ic # type: ignore

class N01Ini:
    _original_ini_from_toml: dict[str, dict[str, str|int]] = {}
    _original_ini_file_with_path: str = ""
    
    _modified_ini_with_imported_schedule: dict[str, dict[str, str|int]] = {}
    _updated_ini_file_with_path: str = ""

    def __init__(self):
        print("Loading n01.ini file")
        
        if not self._select_original_ini_file_path():
            print("No n01.ini file selected")
            return

        if not self._load_original_ini_file():
            print("Error in loading TOML data")
            return
        
        # self._extract_schedule_from_ini()
        
        print("n01.ini file loaded successfully")

    @property
    def ini_file_location(self) -> str:
        return self._original_ini_file_with_path
    
    @property
    def original_ini_data_from_toml(self) -> dict[str, dict[str, str|int]]:
        return self._original_ini_from_toml
    
    def _select_original_ini_file_path(self) -> bool:
        
        title: str = "Select n01.ini file"
        filetypes: list[tuple[str, str]] = [("INI files", "*.ini"), ("TOML files", "*.toml"), ("All files", "*.*")]
        self._original_ini_file_with_path = askopenfilename(title=title, initialdir=".", filetypes=filetypes)
               
        return self._original_ini_file_with_path != ""
        
    def _load_original_ini_file(self) -> bool:
        raw_data_lines: list[str] = []
        raw_data: str = ""
        
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
            print(f"{e}")
            return False
        
        self._original_ini_from_toml=toml.loads(raw_data)
        
        # ic(self._original_ini_from_toml)
        
        # self.save_ini_file("this_is_new1.ini", self._ini_from_toml)

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
            print(f"{e}")
            return False
            
        return True

    def save_ini_with_updated_schedule(self) -> None:
        
        self._select_modified_ini_file_path()
        self._save_ini_file(self._modified_ini_file_with_path, self._modified_ini_with_imported_schedule)
        

class Schedule:
    _original_schedule: dict[str, str|int] = {}
    _orginal_schedule_sorted_by_set: dict[int, dict[str, str|int]] = {}
    
    _schedule_csv_to_import: str = ""
    _imported_schedule: dict[str, str|int] = {}
    _imported_schedule_sorted_by_set: dict[int, dict[str, str|int]] = {}
    
    _schedule_header: list[str] = []
    
    def __init__(self):
        pass
        
    @property
    def original_schedule(self) -> dict[str, str|int]:
        return self._original_schedule
    
    @property
    def imported_schedule(self) -> dict[str, str|int]:
        return self._imported_schedule
    
    # def _extract_schedule_from_ini(self) -> None:
    
    def extract_schedule_from_original_ini(self, data):
        self._schedule_from_ini = data["schedule"]
        # self._original_schedule = data

    def _sort_schedule_from_toml_by_set(self, data: dict[str, str|int]) -> None:
        # Group the data into rounds
        
        for key in data:
            this_set: int = 0
            
            if key == "count":
                continue
            
            this_set = int(key[-3:]) if key[-3:].isnumeric() else int(key[-2:]) if key[-2:].isnumeric() else int(key[-1])
            # if key[-3:].isnumeric():
            #     this_set = int(key[-3:])
            # elif key[-2:].isnumeric():
            #     this_set = int(key[-2:])
            # else:
            #     this_set = int(key[-1])

            if this_set not in self._orginal_schedule_sorted_by_set:
                self._orginal_schedule_sorted_by_set[this_set] = {}
                
            self._orginal_schedule_sorted_by_set[this_set][key] = data[key]

    def _extract_schedule_headers(self) -> None:

        for key in self._orginal_schedule_sorted_by_set[0]:
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
                
                for set in range(len(self._orginal_schedule_sorted_by_set)):
                    this_row_data: dict[str, str|int] = {}
                    for key in self._schedule_header:
                        # The headers do not that the "_0" or "_1" etc 
                        # so this need to be indicated when writing the CSV to ensure it goes to the correct column
                        this_row_data[key] =  self._orginal_schedule_sorted_by_set[set][f"{key}_{set}"]
                    writer.writerow(this_row_data)

        except Exception as e:
            print(f"{e}")
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


def main() -> int:
    ini_file: N01Ini = N01Ini()
    
    # schedule: Schedule = Schedule(ini_file.original_schedule)
    # ic(schedule.original_schedule)
    
    # schedule.save_schedule_as_csv(schedule.original_schedule, "sample_schedule.csv")
    
    schedule: Schedule = Schedule()
    schedule.import_schedule_from_csv()
    
    ini_file.replace_original_schedule_with_imported_schedule(schedule.imported_schedule)
    
    ini_file.save_ini_with_updated_schedule()
    
    return 0


if __name__ in "__main__":
    main()