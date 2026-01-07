## add_sampling_procedure

### About
Enriches the XML document by adding sampling procedure information.  
For each sampling procedure associated with the dataset, the function appends two elements to the XML root:
- `<fresh:SamplingModeFR>`
- `<fresh:SamplingModeEN>`

The values are derived from an external Excel mapping table and may include a reference URI when available.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process. The PEF identifier is inferred from the filename.
- **input_folder** (`str`): Directory containing the source XML file.
- **output_folder** (`str`): Directory where the transformed XML file will be written.
- **context** (optional): Pipeline context providing logger, changelog, and access to shared resources.

### External Files
- **add-sampling-procedure.xlsx**:  
  Excel mapping table linking PEF identifiers to sampling procedure labels.  
  For each PEF ID, the file provides:
  - A French label (`ChampFReSH_fr`)
  - An English label (`ChampFReSH_en`)
  - An optional CESSDA URI (`URI_CESSDA`)  
  Each matching row results in the creation of one French and one English sampling mode element in the XML.

### Output
- The XML file is written to the output folder.
- Zero or more sampling procedure elements may be added, depending on whether mappings exist.
- Each added element may include a `uri` attribute when a CESSDA URI is provided.
- All additions are recorded in the changelog when available.

### How It Works
1. Parses the input XML document.
2. Extracts the PEF identifier from the XML filename.
3. Loads the external Excel mapping table and filters rows matching the PEF identifier.
4. For each matching row:
   - Creates a `<fresh:SamplingModeFR>` element with the French label.
   - Creates a `<fresh:SamplingModeEN>` element with the English label.
   - Adds a `uri` attribute when a CESSDA reference is available.
5. Appends the new elements to the XML root.
6. Writes the updated XML document to the output folder.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **pandas**: Used to load and filter the Excel mapping table.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **os.path.join**: Used to construct paths to external Excel files.
