## update_fundings

### About
Enriches the XML document by adding funding information.  
For each funding entity associated with the dataset, a `<fresh:FundingAgent>` element is appended to the XML root, including standardized names, organization types, and persistent identifiers when available.

The enrichment is driven by a mapping table indexed by the PEF identifier extracted from the XML filename.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process. The PEF identifier is inferred from the filename.
- **input_folder** (`str`): Directory containing the source XML file.
- **output_folder** (`str`): Directory where the transformed XML file will be written.
- **context** (optional): Pipeline context providing logger, changelog, and access to shared resources.

### External Files
- **OK-Financeurs.xlsx**:  
  Excel mapping table linking PEF identifiers to funding organizations.  
  The file provides normalized funder names, organization types (French and English), and optional persistent identifiers such as ROR or SIREN.  
  Each matching row results in the creation of a new funding agent entry in the XML document.

### Output
- The XML file is always written to the output folder.
- Zero or more `<fresh:FundingAgent>` elements may be added depending on the presence of matching entries.
- Each added funding agent may include organization identifiers when available.
- All additions are logged in the changelog when provided.

### How It Works
1. Parses the input XML document.
2. Extracts the PEF identifier from the XML filename.
3. Loads the external Excel mapping table and filters entries for the current PEF identifier.
4. For each matching row:
   - Creates a new `<fresh:FundingAgent>` element.
   - Populates it with standardized funder name and organization type labels.
   - Adds persistent identifiers when available.
5. Appends all generated funding agents to the XML root.
6. Writes the updated XML document to the output folder.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **pandas**: Used to load and filter the Excel mapping table.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **os.path.join**: Used to construct paths to external Excel files.
