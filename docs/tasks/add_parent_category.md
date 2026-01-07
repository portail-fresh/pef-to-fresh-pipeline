## add_parent_category

### About
Normalizes hierarchical category values in the XML by duplicating parent categories.  
When a category value contains a colon (`:`), the function keeps the original value and adds an additional `<value>` element containing only the parent part (the text before the colon).

This is used to ensure that both specific and high-level categories are explicitly present in the metadata.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Directory containing the source XML file.
- **output_folder** (`str`): Directory where the modified XML file will be written.
- **context** (optional): Pipeline context providing logger and changelog utilities.

### Fields Processed
The function scans the entire XML document and processes the following elements, wherever they occur:
- `DomainesDePathologiesFR`
- `DomainesDePathologiesEN`
- `DeterminantsDeSanteFR`
- `DeterminantsDeSanteEN`

Within each of these elements, all child `<value>` nodes are examined.

### Output
- The XML file is always written to the output folder.
- Zero or more `<value>` elements may be added.
- Existing values are never removed or modified; only additional parent values are appended.
- All additions are recorded in the changelog when available.

### How It Works
1. Parses the input XML document.
2. Searches globally for the targeted category elements.
3. For each `<value>` element:
   - Checks whether its text contains a colon (`:`).
   - If so, extracts the substring before the colon.
4. Creates a new `<value>` element containing only this parent category.
5. Appends the new element alongside the original one.
6. Logs each added parent category to the changelog.
7. Writes the updated XML document to the output folder.

### Libraries Used
- **pathlib.Path**: Used to manage file system paths in a platform-independent way.
- **lxml.etree**: Used to parse, traverse, modify, and write XML documents.
