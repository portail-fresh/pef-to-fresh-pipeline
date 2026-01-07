## add_nct_identifier

### About
Enriches the `<Metadonnees>` section of an XML file by adding a `<fresh:ID>` element with the attribute `agency="NCT"` (Clinical Trials), based on the NCT IDs stored in an Excel file. This allows the FReSH system to reference the clinical trial NCT identifier alongside the PEF ID.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process (e.g., `'74131_metadata.xml'`).
- **input_folder** (`str`): Folder containing the original XML file.
- **output_folder** (`str`): Folder where the updated XML file will be saved.
- **context** (optional): Pipeline context providing logger, changelog, and access to the conversion tables folder.

### External Files
- **`nct-repartition.xlsx`**: Excel file mapping PEF IDs to NCT identifiers.
  - Columns:
    - `ID_PEF`: The original PEF identifier corresponding to a study.
    - `ID_NCT`: The NCT identifier to assign to `<fresh:ID>` in the XML.
  - The task reads this file, looks up the PEF ID extracted from the XML filename, and creates a `<fresh:ID>` element with the NCT value if a mapping exists.

### Output Arguments
- Writes the transformed XML file to the output folder, whether or not a mapping is found.
- Logs the addition of the `<fresh:ID>` element in the changelog if a mapping was applied.

### How It Works
1. Extracts the PEF ID from the XML filename (first part before `_`).
2. Loads the Excel mapping to find the corresponding NCT ID.
3. Parses the XML using `lxml.etree`.
4. Finds the `<Metadonnees>` element in the XML.
5. If a mapping exists, appends a `<fresh:ID>` element with `agency="NCT"` and the mapped value.
6. Logs the change to the changelog.
7. Writes the updated XML back to the output folder.

### Libraries Used
- **os.path.join**: Constructs platform-independent file paths.
- **lxml.etree**: For parsing, manipulating, and writing XML files.
- **pandas**: For reading the Excel mapping file.
- **logging**: For logging info and error messages during processing.
