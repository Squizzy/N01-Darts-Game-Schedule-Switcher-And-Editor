# Standard modules
import tkinter as tk # type: ignore
from tkinter import ttk # type: ignore
from tkinter import messagebox

# pip installed modules
from tktooltip import ToolTip # type: ignore 

# app modules
from ini_handler import N01Ini
from schedule_handler import Schedule

class UI:
    _window:tk.Tk
    _buttons_frame:tk.Frame
    _schedule_frame:tk.Frame
    _modify_padx:int
    _modify_pady:int
    _style:ttk.Style
    
    _ini_file:N01Ini
    
    _schedule_original_sorted_by_set:dict[int, dict[str, str|int]] = {}
    _schedule_original_is_loaded:bool = False 
    
    _schedule_modified_sorted_by_set:dict[int, dict[str, str|int]] = {}
    
    _modification_table_columns_widths:dict[str, int] = {}
    
    def __init__(self):
        # initialise Tk window
        self._window = tk.Tk()
        
        # display the window
        self._window.title("N01 Schedule Switcher")
        self._window.configure(background="DarKGreen")
        self._window.minsize(900,600)
        self._window.maxsize(1920,1080)
        self._window.config(width=900, height=600)    
        
        self._buttons_frame = tk.Frame(self._window, bg="yellow", width=890)
        self._schedule_frame = tk.Frame(self._window, bg="lightblue")

        # Pre-define the widths of the table cells
        # Note that this this does not adapt if font is face or size is changed    
        self._modification_table_columns_widths = {
            "set_no": 3,
            "start_score": 6,
            "round_limit": 6,
            "round": 6,
            "max_leg": 4,
            "best_of": 4,
            "change_first": 7,
            "p1_name": 10,
            "p1_start_score": 6,
            "p1_com": 4,
            "p1_com_level": 5,
            "p2_name": 10,
            "p2_start_score": 6,
            "p2_com": 4,
            "p2_com_level": 5,
            "remove?": 8,
        }

        self._load_styles()
        
        self._generate_buttons_frame()   
        
        # turn off all the buttons that can't be used
        self._disable_buttons() 

    def _load_styles(self) -> None:
        self._style = ttk.Style()
        # Buttons frame styles
        self._style.configure("quit.TButton",  # type: ignore
                              background="red", 
                              justify=tk.CENTER, 
                              anchor=tk.CENTER, 
                              bordercolor="gray")
        
        # Schedule frame styles
        self._style.configure("header.TLabel",  # type: ignore
                              background="lightblue",)  
        
        self._modify_padx:int = 2
        self._modify_pady:int = 2
        
        # display schedule styles
        self._style.configure("value.TLabel", # type: ignore
                            #   background="lightblue", )
                              background="white", )
        
        self._style.configure("Custom.TCheckbutton", # type: ignore
                            #   anchor=tk.CENTER, 
                              background="lightblue")

    def _generate_buttons_frame(self) -> None:

        # Generate a frame for the buttons
        # TODO: Is this the best way to place the frame?
        self._buttons_frame.place(x = 10, y = 10)
        
        buttons_width:int = 35
        
        # - Load schedule from ini
        self._load_original_schedule = ttk.Button(self._buttons_frame, text="Load current game schedule", command=self.load_original_ini_schedule, width=buttons_width)
        # - Display original schedule
        self._display_original_schedule = ttk.Button(self._buttons_frame, text="Display current game schedule", command=self.display_original_schedule, width=buttons_width)
        # - Load schedule from csv
        self._load_schedule_from_csv = ttk.Button(self._buttons_frame, text="Load schedule from csv", command=self.load_modified_schedule, width=buttons_width)
        # - Display loaded schedule
        self._display_modified_schedule = ttk.Button(self._buttons_frame, text="Display loaded/modified schedule", command=self.display_modified_schedule, width=buttons_width)
        # - Modify schedule
        self._modify_schedule = ttk.Button(self._buttons_frame, text="Modify loaded schedule", command=self.modify_schedule, width=buttons_width)
        # - Save schedule as csv
        self._save_schedule = ttk.Button(self._buttons_frame, text="Save modified schedule as new CSV", command=self.save_schedule_as_csv, width=buttons_width)
        # - Set modified schedule to game
        self._set_schedule = ttk.Button(self._buttons_frame, text="Use this schedule for the game", command=self.set_schedule_to_ini, width=buttons_width)
        # - quit
        self._quit_app = ttk.Button(self._buttons_frame, text="Quit", command=self.quit, width=20, style="quit.TButton")

        # Add the buttons to the frame
        self._load_original_schedule.grid(    row=0, column=0, columnspan=1, padx=5, pady=2)
        self._display_original_schedule.grid( row=1, column=0, columnspan=1, padx=5, pady=2)

        self._load_schedule_from_csv.grid(    row=0, column=1, columnspan=1, padx=5, pady=2)
        self._display_modified_schedule.grid( row=1, column=1, columnspan=1, padx=5, pady=2)
        self._modify_schedule.grid(           row=2, column=1, columnspan=1, padx=5, pady=2)
        self._save_schedule.grid(             row=3, column=1, columnspan=1, padx=5, pady=2)
        self._set_schedule.grid(              row=3, column=0, columnspan=1, padx=5, pady=2)

        self._quit_app.grid(                  row=1, column=3, columnspan=1, padx=5, pady=2)
   
    def _disable_buttons(self) -> None:
        self._display_original_schedule["state"] = "disabled"
        self._display_modified_schedule["state"] = "disabled"
        self._modify_schedule["state"] = "disabled"
        self._save_schedule["state"] = "disabled"
        self._set_schedule["state"] = "disabled"
        
    def _enable_buttons(self) -> None:
        self._display_original_schedule["state"] = "enabled"
        self._display_modified_schedule["state"] = "enabled"
        self._modify_schedule["state"] = "enabled"
        self._save_schedule["state"] = "enabled"
        self._set_schedule["state"] = "enabled"
    
    def load_original_ini_schedule(self) -> None:
        
        # Load the ini file
        self._ini_file = N01Ini()
        
        # Create a schedule instance
        self._ini_schedule:Schedule = Schedule()

        # Reset the dictionary that will contain the schedule sorted by sets
        self._schedule_original_sorted_by_set = {}

        # Extract the schedule from the original ini file (will be in TOML format)
        if not(self._ini_schedule.extract_toml_schedule_from_original_ini(self._ini_file.original_ini_data_from_toml)):
            return

        # Convert the ini schedule to sorted by set
        self._ini_schedule.convert_schedule_in_toml_to_schedule_sorted_by_set(self._ini_schedule.schedule_original_in_toml)

        # set both the app's original schedule, and the modified schedule, to that schedule coming from the original ini
        self._schedule_original_sorted_by_set = self._ini_schedule.schedule_original_sorted_by_set
        self._schedule_modified_sorted_by_set = self._schedule_original_sorted_by_set.copy()
        
        # Flag that the original schedule is loaded
        if bool(self._schedule_original_sorted_by_set):
            self._schedule_original_is_loaded = True
        
        # Display the schedule table in view-only mode
        self.display_original_schedule()
        
        # As there is a schedule loaded, modification are possible, re-enable the buttons
        self._enable_buttons()

    def load_modified_schedule(self) -> None:
        schedule: Schedule = Schedule()
        
        # Get the schedule to do its magic importing from a csv in sorted by set format
        schedule.import_schedule_from_csv()
        self._schedule_modified_sorted_by_set = schedule.schedule_imported_sorted_by_set
        
        # Display the schedule table in view-only mode
        self.display_modified_schedule()
        
        # As there is a schedule loaded, modification are possible, re-enable the buttons
        self._enable_buttons()
        
    def display_original_schedule(self) -> None:
        # Stub to switch between the original and the modified schedule
        self._create_table_to_view_schedule(self._schedule_original_sorted_by_set)

    def display_modified_schedule(self) -> None:
        # Stub to switch between the original and the modified schedule
        self._create_table_to_view_schedule(self._schedule_modified_sorted_by_set)
        
    def _destroy_schedule_frame(self) -> None:
        # Destroys the schedule frame before displaying a new one (view or modify mode)
        if self._schedule_frame.winfo_exists():
            self._schedule_frame.grid_forget()
            self._schedule_frame.destroy()
    
    def _create_schedule_frame(self) -> None:
        
        # Non-scrollable frame
        self._schedule_frame = tk.Frame(self._window, bg="lightblue")
        self._schedule_frame.place(x = 10, y = 140)
        
        # Scrollable frame
        # Currently not working so not enabled
        # TODO: fix scrollable schedule frame
        # below as per: https://blog.teclado.com/tkinter-scrollable-frames/
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
    
    def _create_table_to_view_schedule(self, schedule:dict[int, dict[str, str|int]] = {}) -> None:
        
        def display_table_add_headers(header_info:list[str], x:int, y:int) -> None:
            for item in header_info:
                header = ttk.Label(self._schedule_frame, 
                                    text=item.replace("_", "\n"), 
                                    width=self._modification_table_columns_widths[item],
                                    justify=tk.CENTER,  
                                    anchor=tk.CENTER,   
                                    # foreground="red",
                                    style="header.TLabel"
                                    )
                
                if item == "set_no" or item == "remove?":
                    header.configure(foreground="red")
                    
                header.grid(row=y, column=x, padx=1, pady=1, sticky=tk.NSEW)
                x += 1        
        
        def display_table_add_line_values(values_info: dict[str, str|int], row_key:int , x:int , y:int) -> None:
            
            for value_info in values_info:
                value:str|int
                if value_info == "set_no":
                    value = row_key
                else:
                    if value_info in ["change_first", "p1_com", "p2_com", "round_limit", "best_of"]:
                        value = "✓" if values_info[value_info] == 1 else "✕"
                    else:
                        value = str(values_info[value_info])
                
                valuebox = ttk.Label(self._schedule_frame, 
                                    text=value, 
                                    width=self._modification_table_columns_widths[value_info], 
                                    anchor=tk.CENTER,
                                    style="value.TLabel"
                                    )
                valuebox.grid(row=y, column=x, padx=1, pady=1)
                x += 1
                
                
            #     value_info = 
            #     ttk.Label(self._schedule_frame, 
            #             text=str(y), 
            #             width=3, 
            #             foreground = "red",
            #             anchor=tk.CENTER,
            #             style="value.TLabel"
            #             )
            #     textbox.grid(row=y, column=x, padx=1, pady=1)
            #     x += 1
                
            # textbox = ttk.Label(self._schedule_frame, 
            #             text=str(y), 
            #             width=3, 
            #             foreground = "red",
            #             anchor=tk.CENTER,
            #             style="value.TLabel"
            #             )
            #     textbox.grid(row=y, column=x, padx=1, pady=1)
            #     x += 1
                
            #     for col_key in schedule[row_key]:
                    
            #         if col_key in ["change_first", "p1_com", "p2_com", "round_limit", "best_of"]:
            #             text_value = "✓" if schedule[row_key][col_key] == 1 else "✕"
            #         else:
            #             text_value = str(schedule[row_key][col_key])
                        
            #         textbox = ttk.Label(self._schedule_frame, 
            #                             text=text_value, 
            #                             width=columns_width[col_key], 
            #                             anchor=tk.CENTER,
            #                             style="value.TLabel"
            #                             )
            #         textbox.grid(row=y, column=x, padx=1, pady=1)
            #         x += 1
            #     y += 1
            #     x = 0
        
        # check if a schedule is loaded (not empty)
        if not bool(schedule):
            messagebox.showwarning(title="Display loaded schedule", message="No schedule loaded to display", icon="warning")
            return

        # if a schedule frame already exists, destroy it
        self._destroy_schedule_frame()

        # Create a new schedule frame
        self._create_schedule_frame()

        # Generate a table of textboxes to display the original schedule
        x = 0
        y = 0
        
        # Add the headers
        header: list[str] = []
        
        header.append("set_no")
        header.extend(schedule[0].keys())
        
        display_table_add_headers(header, x, y)
        
        y += 1
        x = 0

        # Add a line for each of the items
        line_values:dict[str, str|int] = {}
        for row_key in schedule:
            line_values["set_no"] = row_key
            line_values.update(schedule[row_key])
            
            display_table_add_line_values(line_values, row_key, x, y)
            
            y += 1
            x = 0
            
    
    def modify_schedule(self) -> None:
        # Stub for the buttons (lazily not passing the arguments from the button)
        self._create_table_to_modify_loaded_schedule(self._schedule_modified_sorted_by_set)
    
    
    def _create_table_to_modify_loaded_schedule(self, schedule:dict[int, dict[str, str|int]]) -> None:
        
        def modification_table_add_headers(header_info: list[str], x:int, y:int) -> None:
            for item in header_info:
                self._header[x] = ttk.Label(self._schedule_frame, 
                                            text=item.replace("_", "\n"), 
                                            width=self._modification_table_columns_widths[item],
                                            justify=tk.CENTER,  
                                            anchor=tk.CENTER,   
                                            # foreground="red",
                                            style="header.TLabel"
                                            )
                
                if item == "set_no" or item == "remove?":
                    self._header[x].configure(foreground="red")
                    
                self._header[x].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)
                            
                x += 1
        
        def modification_table_add_header_tooltips() -> None:
    
            for i in range(len(self._header)):
                tooltip: str = ""
                header_text = self._header[i]["text"].replace("\n", "_")
                match header_text:
                    case "set_no":
                        tooltip = "Info only:\nSet number"
                        ToolTip(self._header[i], msg=tooltip)
                        continue
                    case "remove?":
                        tooltip = "Deletion Selection\nTick if set to be deleted when pressing delete button"
                        ToolTip(self._header[i], msg=tooltip)
                        continue
                    case _:
                        if header_text in Schedule.schedule_headers:
                            tooltip = Schedule.schedule_headers[header_text]
                            ToolTip(self._header[i], msg=tooltip)
                        else:
                            tooltip = "n/a"
                            ToolTip(self._header[i], msg=tooltip)

        def modification_table_add_values_line(line_info:dict[str, str|int], row_key:int , x:int , y:int) -> None:
            
            com_level_values:list[str] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
            
            # Fill in the data
            first_col_filled:bool = False
            
            for col_key in line_info:
                item_col_width:int = self._modification_table_columns_widths[col_key]
                item_value:str|int = line_info[col_key]
                if first_col_filled:
                    x += 1
            
                match col_key:
                    
                    case "set_no":
                        set_number_label = tk.Label(self._schedule_frame, width=item_col_width, 
                                                                text=item_value, 
                                                                foreground="red",
                                                                anchor=tk.CENTER,
                                                                # style="value.TLabel"
                                                                background="lightblue"
                                                                )
                        set_number_label.grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        first_col_filled = True
                        continue
                    
                    case "start_score":
                        self._start_score_spinbox_var[row_key] = tk.IntVar()
                        self._start_score_spinbox_var[row_key].set(int(item_value))
                        self._start_score_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=item_col_width, 
                                                                textvariable=self._start_score_spinbox_var[row_key], 
                                                                from_=1, to=1001, increment=2)
                        self._start_score_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue
                    
                    case "round_limit":
                        self._round_limit_checkbutton_var[row_key] = tk.BooleanVar()
                        self._round_limit_checkbutton_var[row_key].set(bool(int(item_value)))
                        self._round_limit_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, 
                                                                variable=self._round_limit_checkbutton_var[row_key], 
                                                                onvalue=True, offvalue=False, 
                                                                style="Custom.TCheckbutton")

                        self._round_limit_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue
                    
                    case "round":
                        self._round_spinbox_var[row_key] = tk.IntVar()
                        self._round_spinbox_var[row_key].set(int(item_value))
                        self._round_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=item_col_width, 
                                                                textvariable=self._round_spinbox_var[row_key], 
                                                                from_=1, to=100, increment=1)
                        self._round_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue
                        
                    case "max_leg":
                        self._max_leg_spinbox_var[row_key] = tk.IntVar()
                        self._max_leg_spinbox_var[row_key].set(int(item_value))
                        self._max_leg_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=item_col_width, 
                                                                textvariable=self._max_leg_spinbox_var[row_key], 
                                                                from_=1, to=100, increment=1)
                        self._max_leg_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue
                        
                    case "best_of":
                        self._best_of_checkbutton_var[row_key] = tk.BooleanVar()
                        self._best_of_checkbutton_var[row_key].set(bool(int(item_value)))
                        self._best_of_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, 
                                                                variable=self._best_of_checkbutton_var[row_key], 
                                                                onvalue=True, offvalue=False, 
                                                                style="Custom.TCheckbutton")
                        self._best_of_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue
                        
                    case "change_first":
                        self._change_first_checkbutton_var[row_key] = tk.BooleanVar()
                        self._change_first_checkbutton_var[row_key].set(bool(int(item_value)))
                        self._change_first_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, 
                                                                variable=self._change_first_checkbutton_var[row_key], 
                                                                onvalue=True, offvalue=False, 
                                                                style="Custom.TCheckbutton")
                        self._change_first_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue
                        
                    case "p1_name":
                        self._p1_name_entry_var[row_key] = tk.StringVar()
                        self._p1_name_entry_var[row_key].set(str(item_value))
                        self._p1_name_entry[row_key] = ttk.Entry(self._schedule_frame, width=item_col_width, 
                                                                textvariable=self._p1_name_entry_var[row_key])
                        self._p1_name_entry[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue

                    case "p1_start_score":
                        self._p1_start_score_spinbox_var[row_key] = tk.IntVar()
                        self._p1_start_score_spinbox_var[row_key].set(int(item_value))
                        self._p1_start_score_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=item_col_width, 
                                                                textvariable=self._p1_start_score_spinbox_var[row_key], 
                                                                from_=1, to=1001, increment=2)
                        self._p1_start_score_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue

                    case "p1_com":
                        self._p1_com_checkbutton_var[row_key] = tk.BooleanVar()
                        self._p1_com_checkbutton_var[row_key].set(bool(int(item_value)))
                        self._p1_com_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, 
                                                                variable=self._p1_com_checkbutton_var[row_key], 
                                                                onvalue=True, offvalue=False,  
                                                                style="Custom.TCheckbutton")
                        self._p1_com_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)                    
                        continue

                    case "p1_com_level":
                        self._p1_com_level_spinbox_var[row_key] = tk.IntVar()
                        self._p1_com_level_spinbox_var[row_key].set(int(item_value))
                        self._p1_com_level_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=item_col_width, 
                                                                textvariable=self._p1_com_level_spinbox_var[row_key], 
                                                                from_=1, to=12, increment=1)
                        self._p1_com_level_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue
                        
                    case "p2_name":
                        self._p2_name_entry_var[row_key] = tk.StringVar()
                        self._p2_name_entry_var[row_key].set(str(item_value))
                        self._p2_name_entry[row_key] = ttk.Entry(self._schedule_frame, width=item_col_width, 
                                                                textvariable=self._p2_name_entry_var[row_key])
                        self._p2_name_entry[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue

                    case "p2_start_score":
                        self._p2_start_score_spinbox_var[row_key] = tk.StringVar()
                        self._p2_start_score_spinbox_var[row_key].set(str(item_value))
                        self._p2_start_score_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=item_col_width, 
                                                                textvariable=self._p2_start_score_spinbox_var[row_key], 
                                                                from_=1, to=1001, increment=2)
                        self._p2_start_score_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue

                    case "p2_com":
                        self._p2_com_checkbutton_var[row_key] = tk.BooleanVar()
                        self._p2_com_checkbutton_var[row_key].set(bool(int(item_value)))
                        self._p2_com_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, 
                                                                variable=self._p2_com_checkbutton_var[row_key], 
                                                                onvalue=True, offvalue=False, 
                                                                style="Custom.TCheckbutton")
                        self._p2_com_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)                    
                        continue

                    case "p2_com_level":
                        self._p2_com_level_combobox_var[row_key] = tk.IntVar()
                        self._p2_com_level_combobox_var[row_key].set(0 if int(line_info["p2_com"]) == 0 else int(item_value))
                        self._p2_com_level_combobox[row_key] = ttk.Combobox(self._schedule_frame, width=item_col_width,
                                                                values=com_level_values, 
                                                                textvariable=self._p2_com_level_combobox_var[row_key])
                        self._p2_com_level_combobox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue

                    case "remove?":
                        self._delete_selector_var[row_key] = tk.BooleanVar()
                        self._delete_selector_var[row_key].set(False)
                        self._delete_selector[row_key] = ttk.Checkbutton(self._schedule_frame, 
                                                            variable=self._delete_selector_var[row_key], 
                                                            onvalue=True, offvalue=False, 
                                                            style="Custom.TCheckbutton")
                        self._delete_selector[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                        continue

                    case _:
                        continue                                        
        
        def modification_table_add_new_line() -> None:
        
            new_row_key = len(self._schedule_modified_sorted_by_set)
            empty_schedule_line: dict[str, str|int] = {"start_score": 0,
                                                    "round_limit": 0,
                                                    "round": 0,
                                                    "max_leg": 0,
                                                    "best_of": 0,
                                                    "change_first": 0,
                                                    "p1_name": "",
                                                    "p1_start_score": 0,
                                                    "p1_com": 0,
                                                    "p1_com_level": 0,
                                                    "p2_name": "",
                                                    "p2_start_score": 0,
                                                    "p2_com": 0,
                                                    "p2_com_level": 0,
                                                    }
            
            self._schedule_modified_sorted_by_set[new_row_key] = empty_schedule_line
            self.modify_schedule()
        
        def modification_table_delete_selected_lines() -> None:

            for choice in range(len(self._delete_selector_var)):
                if self._delete_selector_var[choice].get():
                    self._schedule_modified_sorted_by_set.pop(choice)

            new_index:int = 0
            schedule_updated: dict[int, dict[str, str|int]] = {}
            for _, value in self._schedule_modified_sorted_by_set.items():
                schedule_updated[new_index] = value
                new_index += 1

            self._schedule_modified_sorted_by_set = schedule_updated
            self.modify_schedule()
            

        
        if not bool(schedule):
            messagebox.showinfo("request schedule not loaded")
            return

        # if a schedule frame already exists, destroy it
        self._destroy_schedule_frame()

        # Create a new schedule frame
        self._create_schedule_frame()

        # if self._schedule_frame.winfo_exists():
        #     self._schedule_frame.grid_forget()
        #     self._schedule_frame.destroy()
            
        # # Non-scrollable frame
        # self._schedule_frame = tk.Frame(self._window, bg="lightblue")
        # self._schedule_frame.place(x = 10, y = 170)
        
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
        # columns_width = {
        #     "start_score": 6,
        #     "round_limit": 6,
        #     "round": 6,
        #     "max_leg": 4,
        #     "best_of": 4,
        #     "change_first": 7,
        #     "p1_name": 10,
        #     "p1_start_score": 6,
        #     "p1_com": 5,
        #     "p1_com_level": 5,
        #     "p2_name": 10,
        #     "p2_start_score": 6,
        #     "p2_com": 5,
        #     "p2_com_level": 5,
        # }
        
        # com_level_values:list[str] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        
        
        # Define the style for the headers and for the values
        # style:ttk.Style = ttk.Style()
        # self._style.configure("Custom.TCheckbutton", background="lightblue")
        
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
        
        self._delete_selector: dict[int, ttk.Checkbutton] = {}
        self._delete_selector_var: dict[int, tk.BooleanVar] = {}
        
        # self._modify_padx:int = 2
        # self._modify_pady:int = 2
        
        # Generate a table of textboxes to display the original schedule
        x = 0
        y = 0
        
        # Create a label for each header in the schedule
        # self._style.configure("header.TLabel", 
        #         background="lightblue", 
        #         )       
        
        # add Add and Remove buttons # - Load schedule from ini
        self._add_button = ttk.Button(self._schedule_frame, text="Add a line", command=modification_table_add_new_line, width=20)
        self._delete_button = ttk.Button(self._schedule_frame, text="Delete selected lines", command=modification_table_delete_selected_lines, width=20)
        
        self._add_button.grid(row = y, column=4, columnspan=4, pady=self._modify_pady)
        self._delete_button.grid(row = y, column=8, columnspan=4)
        y += 1
        
        header_info: list[str] = []
        header_info.append("set_no")
        # TODO: There is an error with this value below when a csv has not been loaded but a ini has been
        header_info.extend(schedule[0].keys())
        header_info.append("remove?")
        
        modification_table_add_headers(header_info, x, y)
        
        # # Add a column header for a value that does not exist in the schedule
        # self._header[x] = ttk.Label(self._schedule_frame, 
        #             text="set\nno", 
        #             width=3,
        #             justify=tk.CENTER,  
        #             anchor=tk.CENTER,   
        #             foreground="red",
        #             style="header.TLabel"
        #             )
        # self._header[x].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
        # x += 1

        # # Add the headers
        # for key, _ in schedule[0].items():
        #     self._header[x] = ttk.Label(self._schedule_frame, 
        #                        text=str(key).replace("_", "\n"), 
        #                        width=columns_width[key],
        #                        justify=tk.CENTER,  
        #                        anchor=tk.CENTER,
        #                        style="header.TLabel"
        #                        )
        #     self._header[x].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
        #     x += 1
        
        #         # Add a column header for a value that does not exist in the schedule
        # self._header[x] = ttk.Label(self._schedule_frame, 
        #             text="remove?", 
        #             width=7,
        #             justify=tk.CENTER,  
        #             anchor=tk.CENTER,   
        #             foreground="red",
        #             style="header.TLabel"
        #             )
        # self._header[x].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
        
        # x += 1
        
        # Add tooltips on the headers
        modification_table_add_header_tooltips()
        # for i in range(x):
        #     ToolTip(self._header[i], msg=Schedule.schedule_headers[
        #         (self._header[i]["text"]).replace("\n", "_")] if (self._header[i]["text"]).replace("\n", "_") in Schedule.schedule_headers \
        #         else "Info only:\nSet number" if (self._header[i]["text"]).replace("\n", "_") == "set_no" \
        #         else "Deletion Selection\nTick if set to be deleted when pressing delete button" if (self._header[i]["text"]).replace("\n", "_") == "remove?" \
        #         else "n/a")
        
        x = 0
        y += 1
        
        for row_key in schedule:
            modifiable_values_line_info: dict[str, str|int] = {}
            modifiable_values_line_info["set_no"] = (y-1) # The set value, won't be modifiable
            modifiable_values_line_info.update(schedule[row_key])
            modifiable_values_line_info["remove?"] = 0 # Deletion selector tick mark- by default 0 = False (unticked)
            
            modification_table_add_values_line(modifiable_values_line_info, row_key, x, y)
            x = 0
            y += 1
        
        # for row_key in schedule:
        #     # Add the set value (information not in the schedule)
        #     textbox = tk.Label(self._schedule_frame, 
        #             text=str(y-1), 
        #             width=3, 
        #             foreground="red",
        #             anchor=tk.CENTER,
        #             # style="value.TLabel"
        #             background="lightblue"
        #             )
        #     textbox.grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
        #     x += 1
            
        #     # Fill in the data
        #     for col_key in schedule[row_key]:
        #         if col_key == "start_score":
        #             self._start_score_spinbox_var[row_key] = tk.IntVar()
        #             self._start_score_spinbox_var[row_key].set(int(schedule[row_key][col_key]))
        #             self._start_score_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
        #                                                       textvariable=self._start_score_spinbox_var[row_key], from_=1, to=1001, increment=2)
        #             self._start_score_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                    
        #         if col_key == "round_limit":
        #             self._round_limit_checkbutton_var[row_key] = tk.BooleanVar()
        #             self._round_limit_checkbutton_var[row_key].set(bool(int(schedule[row_key][col_key])))
        #             self._round_limit_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, style="Custom.TCheckbutton", width=1,
        #                                                               variable=self._round_limit_checkbutton_var[row_key], onvalue=True, offvalue=False)

        #             self._round_limit_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)
                    
        #         if col_key == "round":
        #             self._round_spinbox_var[row_key] = tk.IntVar()
        #             self._round_spinbox_var[row_key].set(int(schedule[row_key][col_key]))
        #             self._round_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
        #                                                 textvariable=self._round_spinbox_var[row_key], from_=1, to=100, increment=1)
        #             self._round_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                    
        #         if col_key == "max_leg":
        #             self._max_leg_spinbox_var[row_key] = tk.IntVar()
        #             self._max_leg_spinbox_var[row_key].set(int(schedule[row_key][col_key]))
        #             self._max_leg_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
        #                                                   textvariable=self._max_leg_spinbox_var[row_key], from_=1, to=100, increment=1)
        #             self._max_leg_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                    
        #         if col_key == "best_of":
        #             self._best_of_checkbutton_var[row_key] = tk.BooleanVar()
        #             self._best_of_checkbutton_var[row_key].set(bool(int(schedule[row_key][col_key])))
        #             self._best_of_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, style="Custom.TCheckbutton", width=1,
        #                                                           variable=self._best_of_checkbutton_var[row_key], onvalue=True, offvalue=False)
        #             self._best_of_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)
                    
        #         if col_key == "change_first":
        #             self._change_first_checkbutton_var[row_key] = tk.BooleanVar()
        #             self._change_first_checkbutton_var[row_key].set(bool(int(schedule[row_key][col_key])))
        #             self._change_first_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, style="Custom.TCheckbutton", width=1,
        #                                                                variable=self._change_first_checkbutton_var[row_key], onvalue=True, offvalue=False)
        #             self._change_first_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)
                    
        #         if col_key == "p1_name":
        #             self._p1_name_entry_var[row_key] = tk.StringVar()
        #             self._p1_name_entry_var[row_key].set(str(schedule[row_key][col_key]))
        #             self._p1_name_entry[row_key] = ttk.Entry(self._schedule_frame, width=columns_width[col_key], 
        #                                               textvariable=self._p1_name_entry_var[row_key])
        #             self._p1_name_entry[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)

        #         if col_key == "p1_start_score":
        #             self._p1_start_score_spinbox_var[row_key] = tk.IntVar()
        #             self._p1_start_score_spinbox_var[row_key].set(int(schedule[row_key][col_key]))
        #             self._p1_start_score_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
        #                                            textvariable=self._p1_start_score_spinbox_var[row_key], from_=1, to=1001, increment=2)
        #             self._p1_start_score_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)

        #         if col_key == "p1_com":
        #             self._p1_com_checkbutton_var[row_key] = tk.BooleanVar()
        #             self._p1_com_checkbutton_var[row_key].set(bool(int(schedule[row_key][col_key])))
        #             self._p1_com_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame,  style="Custom.TCheckbutton",
        #                                                    variable=self._p1_com_checkbutton_var[row_key], onvalue=True, offvalue=False)
        #             self._p1_com_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)                    

        #         if col_key == "p1_com_level":
        #             self._p1_com_level_spinbox_var[row_key] = tk.IntVar()
        #             self._p1_com_level_spinbox_var[row_key].set(int(schedule[row_key][col_key]))
        #             self._p1_com_level_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
        #                              textvariable=self._p1_com_level_spinbox_var[row_key], from_=1, to=12, increment=1)
        #             self._p1_com_level_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                    
        #         if col_key == "p2_name":
        #             self._p2_name_entry_var[row_key] = tk.StringVar()
        #             self._p2_name_entry_var[row_key].set(str(schedule[row_key][col_key]))
        #             self._p2_name_entry[row_key] = ttk.Entry(self._schedule_frame, width=columns_width[col_key], 
        #                                               textvariable=self._p2_name_entry_var[row_key])
        #             self._p2_name_entry[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)

        #         if col_key == "p2_start_score":
        #             self._p2_start_score_spinbox_var[row_key] = tk.StringVar()
        #             self._p2_start_score_spinbox_var[row_key].set(str(schedule[row_key][col_key]))
        #             self._p2_start_score_spinbox[row_key] = ttk.Spinbox(self._schedule_frame, width=columns_width[col_key], 
        #                                            textvariable=self._p2_start_score_spinbox_var[row_key], from_=1, to=1001, increment=2)
        #             self._p2_start_score_spinbox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)

        #         if col_key == "p2_com":
        #             self._p2_com_checkbutton_var[row_key] = tk.BooleanVar()
        #             self._p2_com_checkbutton_var[row_key].set(bool(int(schedule[row_key][col_key])))
        #             self._p2_com_checkbutton[row_key] = ttk.Checkbutton(self._schedule_frame, style="Custom.TCheckbutton",
        #                                                    variable=self._p2_com_checkbutton_var[row_key], onvalue=True, offvalue=False)
        #             self._p2_com_checkbutton[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady, sticky=tk.NSEW)                    

        #         if col_key == "p2_com_level":
        #             self._p2_com_level_combobox_var[row_key] = tk.IntVar()
        #             self._p2_com_level_combobox_var[row_key].set(0 if int(schedule[row_key]["p2_com"]) == 0 else int(schedule[row_key][col_key]))
        #             self._p2_com_level_combobox[row_key] = ttk.Combobox(self._schedule_frame, width=columns_width[col_key],
        #                                                           values=com_level_values, textvariable=self._p2_com_level_combobox_var[row_key])
        #             self._p2_com_level_combobox[row_key].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
                                        
        #         x += 1
            
        #     # add delete line selector
        #     self._delete_selector_var[y - 1] = tk.BooleanVar()
        #     self._delete_selector_var[y - 1].set(False)
        #     self._delete_selector[y - 1] = ttk.Checkbutton(self._schedule_frame, style="Custom.TCheckbutton", width=3,
        #                                                               variable=self._delete_selector_var[y - 1], onvalue=True, offvalue=False)
        #     self._delete_selector[y - 1].grid(row=y, column=x, padx=self._modify_padx, pady=self._modify_pady)
        #     y += 1
        #     x = 0
        
    def _read_table_of_modified_values(self) -> None:
        
        self._schedule_modified_sorted_by_set = {}
        number_of_entries = len(self._start_score_spinbox_var)
        
        for row_key in range(number_of_entries):
            self._schedule_modified_sorted_by_set[row_key] = {}
            self._schedule_modified_sorted_by_set[row_key]["start_score"] = int(self._start_score_spinbox_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["round_limit"] = bool(self._round_limit_checkbutton_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["round"] = int(self._round_spinbox_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["max_leg"] = int(self._max_leg_spinbox_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["best_of"] = bool(self._best_of_checkbutton_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["best_of"] = bool(self._change_first_checkbutton_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["p1_name"] = str(self._p1_name_entry_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["p1_start_score"] = int(self._p1_start_score_spinbox_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["p1_com"] = bool(self._p1_com_checkbutton_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["p1_com_level"] = int(self._p1_com_level_spinbox_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["p2_name"] = str(self._p2_name_entry_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["p2_start_score"] = int(self._p2_start_score_spinbox_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["p2_com"] = bool(self._p2_com_checkbutton_var[row_key].get())
            self._schedule_modified_sorted_by_set[row_key]["p2_com_level"] = int(self._p2_com_level_combobox_var[row_key].get())
    
    
    def save_schedule_as_csv(self) -> None:
        schedule: Schedule = Schedule()
        
        
        if hasattr(self, "_start_score_spinbox"):
            self._read_table_of_modified_values()
        else:
            # currently below left while for debug, but should not be needed
            messagebox.showwarning(title="error", message="No modifications has been attempted, no change to read")
            
        schedule.save_modified_schedule_as_csv(self._schedule_modified_sorted_by_set)

    def set_schedule_to_ini(self) -> None:

        # Check if there is a modified schedule, if not, abort        
        if not hasattr(self, "_modified_schedule") or not bool(self._schedule_modified_sorted_by_set):
            messagebox.showwarning(title="Modified schedule", message="No schedule loaded - aborting", icon="warning")
            return
        
        # Instantiate a schedule
        schedule: Schedule = Schedule()

        # If no ini file has been loaded, request the ini file
        if not hasattr(self, "_ini_file"):
            self._ini_file = N01Ini()
        
        # Abort if no ini file is selected
        if not hasattr(self, "_ini_file"):
            messagebox.showwarning(title="Ini file to save to", message="No ini file selected to store the schedule. Aborting", icon="warning")
            return
            
        # If there are modifications to the schedule, read the latest version
        if bool(self._start_score_spinbox_var):
            self._read_table_of_modified_values()

        # Transfer the modified schedule to the Schedule
        schedule.store_schedule_modifications(self._schedule_modified_sorted_by_set)
        
        # Convert it to a schedule in TOML format
        schedule.convert_modified_schedule_sorted_by_set_to_toml_schedule()
        
        # Send that TOML schedule to the ini handler
        self._ini_file.replace_original_schedule_with_imported_schedule(schedule.schedule_modified_in_toml)
        
        # Save the ini with the updated schedule
        self._ini_file.save_ini_with_updated_schedule()
    
    def quit(self)-> None:
        self._window.destroy()
    
    @property
    def start(self) -> None:
        self._window.mainloop()
