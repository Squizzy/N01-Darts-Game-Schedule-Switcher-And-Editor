# N01 Schedule Switcher and Generator

## The app

This is aimed to be a schedule switcher and schedule exporter/importer for N01 Darts Score application, windows version.  
The game score keeper app is not provided. it can be downloaded as their [author's page - nakka.com](https://nakka.com/soft/n01/index_eng.html): 


## How to use

- Place the .exe file in the same folder as the n01.exe from nakka.com.
- Launch and follow the instructions

### Schedule switcher (option 1)
- This allows to select a pre-made ini-file with a custom schedule and set it as the game's next n01.ini

### Schedule exporter (option 2)
- Export the current schedule as is stored by the app into a CSV file. 
  - This CSV file can be saved as a backup

- More importantly this CSV serves as a file that can 
  - be edited in Excel or Libreoffice to make new schedule from. 
  - It will need to be saved back as CSV. 
  - Multiple copies with different schedules can be made (one schedule per CSV)
    
### Schedule importer (option 3)
- Import the modifed schedule(s) to use by the game
- each import will create a new file named <date>-<time>-<csv name>-n01.ini (so a new one is created at each import, even if the same file is imported again)
- these file can be renamed to n01.ini to replace the game file, but the schedule switcher does this for you

## Releases

- 2025091 - v0.1.0 - Initial release

## License
- GPL-v2

## Comments, questions, suggestions
- raise an issue on the Github page