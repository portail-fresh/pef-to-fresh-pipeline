## process_inclusion_criteria

### About
This task applies field-level transformations to an XML file based on a mapping provided in an Excel file. It is typically used to process inclusion or exclusion criteria in study-related XML records.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Directory containing the input XML file.
- **output_folder** (`str`): Directory where the processed XML file will be saved.
- **context** (optional): Pipeline context providing access to logging and a changelog system.

### Output Arguments
- Saves the transformed XML file to the specified output folder.
- Returns nothing explicitly; success/failure is logged.

### How It Works
1. Reads and parses the XML file.
2. Extracts a `file_id` from the XML file name to identify the appropriate mapping.
3. Loads the Excel mapping file (`new-clusion.xlsx`) that defines transformations at the field level.
4. Uses the `FieldTransformer` utility to apply transformations to the XML tree:
   - Each matching field in the XML is updated according to the Excel rules.
   - Changes are logged in the provided changelog (if available).
5. Writes the updated XML to the output folder, preserving pretty formatting and XML declaration.
6. Logs each step and any errors encountered.

### Notes
- The task will skip processing if the XML file does not exist, cannot be parsed, or the changelog is unavailable.
- Designed to work generically with any XML structure where field-level transformations are required.
- Idempotent: re-running the task will re-apply the same mapping without duplicating data.

### External Dependencies
- Excel mapping file: `new-clusion.xlsx`
