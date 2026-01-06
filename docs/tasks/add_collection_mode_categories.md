## add_collection_mode_categories

### About
Adds collection mode information to an XML file by creating `<CollectionModeFR>` and `<CollectionModeEN>` elements in the FReSH namespace. Each element may include a URI extracted from an Excel mapping.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Folder containing the original XML file.
- **output_folder** (`str`): Folder where the updated XML file will be saved.
- **context** (optional): Pipeline context providing logger and changelog utilities.

### External Files
- **`new-collection-modes.xlsx`**: Excel file providing the mapping between file IDs and collection modes.
  - `PEF_ID`: Used to filter rows for the current XML file.
  - `ChampFReSH_fr`: French label for the collection mode.
  - `ChampFReSH_en`: English label for the collection mode.
  - `URI_CESSDA`: Optional URI associated with the collection mode.  
  This file determines which `<CollectionModeFR>` and `<CollectionModeEN>` elements are added and, when available, sets the `uri` attribute.

### Output Arguments
- Saves the updated XML file to the output folder.
- Logs additions to the changelog for each new `<CollectionModeFR>` and `<CollectionModeEN>` element.

### How It Works
1. Parses the input XML using `lxml.etree`.
2. Reads the Excel mapping and filters rows for the current file ID.
3. For each matching row:
   - Creates `<CollectionModeFR>` and `<CollectionModeEN>` elements in the FReSH namespace.
   - Sets the text content to the French and English labels.
   - Sets the `uri` attribute if a URI is provided.
   - Logs the addition to the changelog.
4. Writes the enriched XML back to the output folder with pretty formatting and XML declaration.

### Libraries Used
- **pathlib.Path**: For platform-independent file path handling.
- **lxml.etree**: To parse, manipulate, and write XML documents.
- **pandas**: To read and filter the Excel mapping file.
- **os.path.join**: To build file paths.
