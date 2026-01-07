## update_sponsor

### About
Enriches the XML document by adding sponsor information.  
For each sponsor associated with the dataset, a `<fresh:Sponsor>` element is appended to the XML root, including the standardized organization name, sponsor type labels in French and English, and optional persistent identifiers.

The enrichment is driven by an Excel mapping table indexed by the PEF identifier extracted from the XML filename.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process. The PEF identifier is inferred from the filename.
- **input_folder** (`str`): Directory containing the source XML file.
- **output_folder** (`str`): Directory where the transformed XML file will be written.
- **context** (optional): Pipeline context providing logger, changelog, and access to shared resources.

### External Files
- **OK_StatutOrganismeSplit.xlsx**:  
  Excel mapping table linking PEF identifiers to sponsor organizations.  
  The file provides normalized sponsor names, sponsor type labels in French and English, and optional organization identifiers such as ROR or SIRET.  
  Each matching row results in the creation of a new sponsor entry in the XML document.

### Output
- The XML file is always written to the output folder.
- Zero or more `<fresh:Sponsor>` elements may be added depending on the presence of matching entries.
- Each sponsor entry may include one or more persistent identifiers.
- All additions are logged in the changelog when available.

### How It Works
1. Parses the input XML document.
2. Extracts the PEF identifier from the XML filename.
3. Loads the external Excel mapping table and filters rows matching the PEF identifier.
4. For each matching row:
   - Creates a new `<fresh:Sponsor>` element.
   - Populates sponsor name and sponsor type labels (FR and EN).
   - Adds organization identifiers when available.
5. Appends each sponsor element to the XML root.
6. Writes the updated XML document to the output folder.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **pandas**: Used to load and filter the Excel mapping table.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **os.path.join**: Used to construct paths to external Excel files.
