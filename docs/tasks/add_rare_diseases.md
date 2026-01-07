## add_rare_diseases

### About
Enriches biobank-related XML content by adding  `<RareDiseases>` nodes. This allows tracking rare diseases as boolean flags in the XML.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Folder containing the original XML file.
- **output_folder** (`str`): Folder where the updated XML file will be saved.
- **context** (optional): Pipeline context providing logger and changelog utilities.

### External Files
- **`rare-diseases-repartition.xlsx`**: Excel file containing mapping rules for rare diseases.
  - Used by `FieldTransformer` to identify which values should be replaced in the XML.
  - Ensures consistent boolean flags for rare disease fields across files.

### Output Arguments
- Saves the transformed XML file to the output folder.
- Logs changes to the changelog for each field modified according to the Excel mapping.

### How It Works
1. Parses the input XML using `lxml.etree`.
2. Uses `FieldTransformer` with the Excel mapping to replace relevant PEF values with FReSH values inside `<ContenuBiothequeFR>` nodes.
3. Writes the updated XML back to the output folder with pretty formatting and XML declaration.
4. Logs all applied transformations in the changelog.

### Libraries Used
- **pathlib.Path**: For platform-independent file path handling.
- **lxml.etree**: To parse, manipulate, and write XML documents.
- **FieldTransformer**: Custom utility responsible for applying field-level transformations based on Excel mapping tables.
