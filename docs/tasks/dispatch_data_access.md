## dispatch_data_access

### About
Applies field-level transformations to XML files specifically targeting data access fields. The transformations ensure consistency of field values according to the FReSH standard.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Directory containing the input XML file.
- **output_folder** (`str`): Directory where the transformed XML file will be saved.
- **context** (optional): Pipeline context providing access to a logger and a changelog system.

### External Files
- **`dispatch-data-access-fr-en.xlsx`**: Excel mapping file containing PEF-to-FReSH replacements for data access fields.  
  Structure:
  - `PEF_value`: original value in the XML  
  - `FReSH_value`: corresponding standardized value  
  - Optional language-specific columns (`FR`/`EN`) for text replacements.  
  This file drives the actual transformations applied to the XML nodes.

### Output Arguments
- Saves the transformed XML file to the output folder.
- Logs all transformations in the changelog if available.

### How It Works
1. Reads and parses the input XML file using `lxml.etree`.
2. Extracts a `file_id` from the XML file name to associate the correct mapping.
3. Loads the Excel mapping file using `pandas`.
4. Uses `FieldTransformer` to apply the mappings to the XML, updating values and recording changes in the changelog.
5. Writes the updated XML with pretty formatting and XML declaration.
6. Logs progress and any errors encountered during processing.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on Excel mapping tables.
