## add_authorizing_agency

### About
Enriches the XML document by applying field-level transformations related to the authorizing agency.  
The task relies on a generic transformation mechanism driven by an external Excel mapping table and delegates all XML modifications to the `FieldTransformer` utility.

The transformation is applied in “general” mode, meaning it is not bound to a specific XML node structure explicitly defined in this task.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process. The PEF identifier is inferred from the filename.
- **input_folder** (`str`): Directory containing the source XML file.
- **output_folder** (`str`): Directory where the transformed XML file will be written.
- **context** (optional): Pipeline context providing logger, changelog, and access to shared resources.

### External Files
- **auth-agency-repartition.xlsx**:  
  Excel mapping table defining how authorizing agency information must be added or aligned.  
  The file is consumed by the `FieldTransformer`, which applies the mappings to the XML document according to its internal rules.

### Output
- The XML file is written to the output folder after transformation.
- All applied changes are logged in the changelog when available.

### How It Works
1. Parses the input XML document.
2. Extracts the PEF identifier from the filename (not directly used in general mode).
3. Initializes a `FieldTransformer` with:
   - the Excel mapping file
   - the current file identifier
   - the task name
   - the changelog instance
4. Applies all transformations defined in the Excel mapping to the XML tree.
5. Writes the updated XML document to the output folder.

### Libraries Used
- **pathlib.Path**: Used to manage input and output file paths.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on Excel mapping tables.
