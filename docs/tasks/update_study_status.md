## update_study_status

### About
This task updates or creates `<EnActiviteFR>` and `<EnActiviteEN>` elements in an XML file based on an external Excel mapping. These elements indicate whether a study is currently active or not. If no mapping exists for the XML's file ID, default values are used (`"Inconnu"` / `"Unknown"`).

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Folder containing the XML file.
- **output_folder** (`str`): Folder where the updated XML file will be written.
- **context** (`optional`): Pipeline context providing access to logger, changelog, and the folder containing Excel mapping tables.

### Output Arguments
- Returns the path to the updated XML file after modifications.

### How It Works
1. Parses the XML file and locates all existing `<EnActiviteFR>` and `<EnActiviteEN>` elements anywhere in the XML tree.
2. Determines the file ID from the XML filename.
3. Reads the Excel mapping (`study-status.xlsx`) to retrieve the French (`ChampFReSH_fr`) and English (`ChampFReSH_en`) status values for that file ID.
4. If no mapping is found, defaults to `"Inconnu"` for French and `"Unknown"` for English.
5. Replaces existing `<EnActiviteFR>`/`<EnActiviteEN>` elements with the mapped values or creates them under the root if none exist.
6. Logs changes in the pipeline changelog if available.
7. Writes the updated XML file to the output folder with proper formatting.

### External Files
- **study-status.xlsx**: Contains the mapping of file IDs (`PEF_ID`) to study status in French and English.

### Libraries Used
- **lxml.etree**: For XML parsing, modification, and writing.
- **pandas**: For reading and handling Excel mapping files.
