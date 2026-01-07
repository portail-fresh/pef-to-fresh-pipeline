## add_metadata_contributors

### About
Enriches the XML document by adding metadata contributor information using an external Excel mapping table.  
Before applying new values, any existing metadata contributor elements in the FReSH namespace are removed to avoid duplication or inconsistency.

All insertions and replacements are delegated to the generic `FieldTransformer`, which applies the mapping rules defined in the Excel file.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process. The PEF identifier is inferred from the filename.
- **input_folder** (`str`): Directory containing the source XML file.
- **output_folder** (`str`): Directory where the transformed XML file will be written.
- **context** (optional): Pipeline context providing logger, changelog, and access to shared resources.

### External Files
- **Contributeurs_arricchito_pids.xlsx**:  
  Excel mapping table defining how metadata contributor information must be added to the XML document.  
  The file is interpreted by the `FieldTransformer`, which applies the mapped values to the appropriate XML elements.

### Output
- The XML file is written to the output folder after transformation.
- All additions are recorded in the changelog when available.

### How It Works
1. Parses the input XML document.
2. Registers the `fresh` namespace if not already present.
3. Removes existing metadata contributor elements in the FReSH namespace to ensure a clean state.
4. Extracts the PEF identifier from the filename.
5. Initializes a `FieldTransformer` with:
   - the Excel mapping file
   - the current file identifier
   - the task name
   - the changelog instance
6. Applies all transformations defined in the Excel mapping.
7. Writes the updated XML document to the output folder.

### Libraries Used
- **pathlib.Path**: Used to manage input and output file paths.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **os.path**: Used to build paths to external Excel mapping files.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on Excel mapping tables.
