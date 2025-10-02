from tkinter import messagebox
# import toml # type: ignore
import csv
from tkinter.filedialog import askopenfilename, asksaveasfilename

class Schedule:
    _schedule_original_in_toml:dict[str, str|int] = {}
    _schedule_original_sorted_by_set:dict[int, dict[str, str|int]] = {}
    
    _csv_filename_of_schedule_to_import:str = ""
    _schedule_imported_in_toml:dict[str, str|int] = {}
    _schedule_imported_sorted_by_set:dict[int, dict[str, str|int]] = {}
    
    _schedule_header:list[str] = []
    
    _schedule_modified_sorted_by_set:dict[int, dict[str, str|int]] = {}
    _schedule_modified_in_toml:dict[str, str|int] = {}
    
    _csv_filename_to_save_modified_schedule: str
    
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
    def schedule_original_in_toml(self) -> dict[str, str|int]:
        return self._schedule_original_in_toml
    
    @property
    def schedule_original_sorted_by_set(self) -> dict[int, dict[str, str|int]]:
        return self._schedule_original_sorted_by_set
    
    @property
    def schedule_imported_in_toml(self) -> dict[str, str|int]:
        return self._schedule_imported_in_toml
    
    @property
    def schedule_modified_in_toml(self) -> dict[str, str|int]:
        return self._schedule_modified_in_toml
    
    @property
    def schedule_imported_sorted_by_set(self) -> dict[int, dict[str, str|int]]:
        return self._schedule_imported_sorted_by_set

    
    def extract_toml_schedule_from_original_ini(self, data: dict[str, dict[str, str|int]]) -> bool:

        if "schedule" not in data:
            # this should never happen normally!
            messagebox.showerror(title="Extracting schedule from n01.ini file", message="Error extracting schedule from ini file:\nThe schedule section is missing.", icon="error")
            return False

        self._schedule_original_in_toml = data["schedule"]
        return True


    def convert_schedule_in_toml_to_schedule_sorted_by_set(self, data: dict[str, str|int]) -> None:
        # Group the data into rounds
        self._schedule_original_sorted_by_set = {}
        
        for key in data:
            this_set: int = 0
            
            if key == "count":
                continue
            
            # The number of the set is stored at the end of each variable name (key) eg "round_12"
            # this_set will extract the integer between 1 and 3 digits that represents the set (set = line in a schedule)
            this_set = int(key[-3:]) if key[-3:].isnumeric() else int(key[-2:]) if key[-2:].isnumeric() else int(key[-1])

            # Create the key if needed
            if this_set not in self._schedule_original_sorted_by_set:
                self._schedule_original_sorted_by_set[this_set] = {}
            
            # Store the set
            self._schedule_original_sorted_by_set[this_set][key[:-(len(str(this_set)) + 1)]] = data[key]

    
    def convert_modified_schedule_sorted_by_set_to_toml_schedule(self) -> bool:
        # Convert the imported schedule to a toml string
        
        # Reset the toml dictionary
        self._schedule_modified_in_toml = {}
        
        # Insert the count value
        self._schedule_modified_in_toml["count"] = len(self._schedule_modified_sorted_by_set)
        
        # Add all the elements of all the sets, restoring the key value to the original one (eg from set 12 of "round" -> "round_12" )
        for set in self._schedule_modified_sorted_by_set:
            for key in self._schedule_modified_sorted_by_set[set]:
                self._schedule_modified_in_toml[f"{key}_{set}"] = self._schedule_modified_sorted_by_set[set][key]
                
        return True


    def import_schedule_from_csv(self) -> bool:

        def load_schedule_from_csv_sorted_by_sets() -> bool:
            
            def select_schedule_csv_file_to_load() -> bool:
                
                title: str = "Select the schedule file to import"
                filetypes: list[tuple[str, str]] = [("CSV files", "*.csv"), ("All files", "*.*")]
                self._csv_filename_of_schedule_to_import = askopenfilename(title=title, initialdir=".", filetypes=filetypes)
                    
                return self._csv_filename_of_schedule_to_import != ""
                       
            if not select_schedule_csv_file_to_load():
                return False
            
            # Reset the dictionary containing the data sorted by set
            self._schedule_imported_sorted_by_set = {}
            
            try:
                with open(self._csv_filename_of_schedule_to_import, "r") as f:
                    reader = csv.DictReader(f)
                    
                    row: dict[str, str|int]
                    set = 0
                    for row in reader:
                        this_set = row
                    
                        # create the round key
                        if set not in self._schedule_imported_sorted_by_set:
                            self._schedule_imported_sorted_by_set[set] = {}
                    
                        # import the values as int or str as needed
                        for key in this_set:
                            if str(this_set[key]).isnumeric():
                                self._schedule_imported_sorted_by_set[set][key] = int(this_set[key])
                            else:
                                if '"' in str(row[key]):
                                    row[key] = str(row[key]).replace('"', '')
                                    
                                self._schedule_imported_sorted_by_set[set][f"{key}"] = row[key]
                        
                        set += 1
                
            except FileNotFoundError as e:
                messagebox.showerror(title="CSV file to import", 
                                     message=f"file {self._csv_filename_of_schedule_to_import} not found:\n{e}", 
                                     icon="error")
                return False
            
            return True

        def convert_imported_schedule_to_toml_schedule() -> bool:
            # Convert the imported schedule to a toml string
            
            for set in self._schedule_imported_sorted_by_set:
                for key in self._schedule_imported_sorted_by_set[set]:
                    self._schedule_imported_in_toml[f"{key}_{set}"] = self._schedule_imported_sorted_by_set[set][key]
                    
            return True

    
        if not load_schedule_from_csv_sorted_by_sets():
            return False

        if not convert_imported_schedule_to_toml_schedule():
            return False
        
        return True


    def store_schedule_modifications(self, update_sorted_by_set: dict[int, dict[str, str|int]]) -> None:
        self._schedule_modified_sorted_by_set = update_sorted_by_set
    
    
    def save_modified_schedule_as_csv(self, data: dict[int, dict[str, str|int]]) -> bool:
        
        def select_filename_to_save_modified_schedule_as_csv() -> bool:
        
            title: str = "Select filename to save the schedule file to csv as"
            filetypes: list[tuple[str, str]] = [("CSV files", "*.csv"), ("All files", "*.*")]
            self._csv_filename_to_save_modified_schedule = asksaveasfilename(title=title, initialdir=".", filetypes=filetypes)
                
            return self._csv_filename_to_save_modified_schedule != ""
    
        def write_data_to_csv_file(data: dict[int, dict[str, str|int]]) -> bool:
            
            # Get the headers from the first line of data
            headers: list[str] = [*data[0]]
        
            # Save the CSV data
            try:        
                with open(self._csv_filename_to_save_modified_schedule, "w", newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    
                    for set in range(len(data)):
                        this_row_data: dict[str, str|int] = {}
                        for header in headers:
                            this_row_data[header] =  data[set][header]
                        writer.writerow(this_row_data)

            except Exception as e:
                messagebox.showerror(title="Saving schedule to CSV file", 
                                     message=f"Error saving schedule to CSV:\n{e}", 
                                     icon="error")
                return False
            
            return True
        
        self._schedule_modified_sorted_by_set = data.copy()
        
        # Select the file to save to
        if not select_filename_to_save_modified_schedule_as_csv():
            messagebox.showinfo(title="CSV filename to save schedule", 
                                message="No filename selected.\naborting save.",
                                icon="info")
            return False
        
        # Add the extension if not there by default
        if self._csv_filename_to_save_modified_schedule[-4:] != ".csv":
            self._csv_filename_to_save_modified_schedule += ".csv"
        
        return write_data_to_csv_file(self._schedule_modified_sorted_by_set)        




    
    # def save_schedule_as_csv(self, data: dict[str, str|int], filename: str) -> bool:

    #     def extract_schedule_headers() -> None:

    #         for key in self._original_schedule_sorted_by_set[0]:
    #             self._schedule_header.append(key[:-2])

        
    #     # turn the dict into a list of strings to be saved
    #     untomled_list: list[str] = toml.dumps(data).splitlines()
        
    #     # remove the stubs for the entries without values
    #     untomled_list = list(map(lambda line: line[:-5] if line.endswith('"|||"') else line, untomled_list))

    #     # Extract the headers
    #     self.convert_schedule_in_toml_to_schedule_sorted_by_set(data)
    #     extract_schedule_headers()

    #     # Save the CSV data
    #     try:        
    #         with open(filename, "w", newline='') as f:
    #             writer = csv.DictWriter(f, fieldnames=self._schedule_header)
    #             writer.writeheader()
                
    #             for set in range(len(self._original_schedule_sorted_by_set)):
    #                 this_row_data: dict[str, str|int] = {}
    #                 for key in self._schedule_header:
    #                     # The headers do not that the "_0" or "_1" etc 
    #                     # so this need to be indicated when writing the CSV to ensure it goes to the correct column
    #                     this_row_data[key] =  self._original_schedule_sorted_by_set[set][f"{key}_{set}"]
    #                 writer.writerow(this_row_data)

    #     except Exception as e:
    #         messagebox.showerror(title="Error saving schedule csv file", message=f"error: {e}")
    #         return False
                    
    #     return True