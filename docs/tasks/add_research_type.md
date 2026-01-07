## add_research_type

### About
Enriches an XML file by adding two `<fresh:ResearchType>` elements to the root, specifying that the study is observational. These elements are always added, regardless of existing content.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Folder containing the XML file.
- **output_folder** (`str`): Folder where the updated XML file will be saved.
- **context** (optional): Pipeline context providing logger and changelog functionality.

### External Files
This task does not require external mapping files; all values are fixed.

### Output Arguments
- Writes the updated XML file to the output folder.
- Logs the addition of `<fresh:ResearchTypeFR>` and `<fresh:ResearchTypeEN>` in the changelog.

### How It Works
1. Parses the XML file using `lxml.etree`.
2. Ensures the `fresh` namespace is registered.
3. Creates:
   - `<fresh:ResearchTypeFR>` with text `"Etude observationnelle"`.
   - `<fresh:ResearchTypeEN>` with text `"Observational Study"`.
4. Appends both elements to the root of the XML.
5. Logs the additions if a changelog is available.
6. Writes the transformed XML back to the output folder.

### Libraries Used
- **os.path.join**: Constructs platform-independent file paths.
- **lxml.etree**: For parsing, manipulating, and writing XML files.
- **logging**: For logging progress and errors during processing.
