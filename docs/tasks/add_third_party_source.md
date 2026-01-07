## add_third_party_source

### About
Enriches the XML document by indicating whether the dataset integrates third-party data.  
The task always adds a `<fresh:IsDataIntegration>` element and conditionally adds a `<fresh:ThirdPartySource>` element when a matching entry is found in the external Excel mapping.

The logic is driven by the PEF identifier extracted from the XML filename.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process. The PEF identifier is inferred from the filename.
- **input_folder** (`str`): Directory containing the source XML file.
- **output_folder** (`str`): Directory where the transformed XML file will be written.
- **context** (optional): Pipeline context providing logger, changelog, and access to shared resources.

### External Files
- **add-third-party-source.xlsx**:  
  Excel mapping table associating PEF identifiers with third-party source labels in French and English.  
  The presence of a matching row determines whether the XML is marked as integrating third-party data and, if so, which source labels are added.

### Output
- The XML file is always written to the output folder.
- A `<fresh:IsDataIntegration>` element is always added.
- A `<fresh:ThirdPartySource>` element is added only when a matching PEF identifier is found in the Excel file.
- All additions are recorded in the changelog when available.

### How It Works
1. Parses the input XML document.
2. Registers the `fresh` namespace if not already present.
3. Extracts the PEF identifier from the XML filename.
4. Loads the Excel mapping file and searches for a row matching the PEF identifier.
5. Appends a `<fresh:IsDataIntegration>` element:
   - `"true"` if a match exists in the Excel file
   - `"false"` otherwise
6. If a match exists, appends a `<fresh:ThirdPartySource>` element populated with the mapped French and English values.
7. Writes the updated XML document to the output folder.

### Libraries Used
- **pathlib.Path**: Used to manage input and output file paths.
- **pandas**: Used to load and filter the Excel mapping table.
- **lxml.etree**: Used to parse, manipulate, and write XML documents.
- **os.path.join**: Used to construct paths to external Excel files.
