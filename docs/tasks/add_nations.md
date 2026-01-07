## add_nations

### About
Enriches the XML document by adding nation information derived from an external Excel mapping.  
For each matching nation, the task appends both a French and an English representation at the root level of the XML, using the FReSH namespace.

Each nation is represented by:
- a human-readable label
- an associated ISO-based URI

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process. The PEF identifier is inferred from the filename.
- **input_folder** (`str`): Directory containing the source XML file.
- **output_folder** (`str`): Directory where the enriched XML file will be written.
- **context** (optional): Pipeline context providing logger, changelog, and access to conversion tables.

### External Files
- **add-nations.xlsx**:  
  Excel mapping table used to determine which nations must be added for a given PEF identifier.  
  Each row links a PEF ID to:
  - an ISO country code
  - a French label
  - an English label  

  Only rows matching the current file’s PEF ID are applied.

### Output
- The XML file is written to the output folder.
- One or more nation elements may be appended to the root element.
- Each added value and URI is recorded in the changelog when available.

### How It Works
1. Parses the input XML document.
2. Extracts the PEF identifier from the filename.
3. Loads the Excel mapping file containing nation definitions.
4. Filters the mapping rows corresponding to the current PEF ID.
5. For each matching row:
   - Adds a French nation element with label and ISO URI.
   - Adds an English nation element with label and ISO URI.
6. Logs each added value to the changelog.
7. Writes the enriched XML document to the output folder.

### Libraries Used
- **pathlib.Path**: Used to manage input and output file paths.
- **pandas**: Used to load and filter the Excel mapping table.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **FieldTransformer**: Imported but not used in this task.
