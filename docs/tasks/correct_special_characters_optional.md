## correct_special_characters_optional

### About
This task cleans textual content inside an XML file by normalizing specific special characters and decoding HTML entities. It is intended as an optional refinement step to improve the readability and usability of text fields after basic XML validation has already been performed.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the cleaned XML file will be saved.

### Output Arguments
- **output_file_path** (`str`): Full path to the cleaned XML file written to the output folder.

### How It Works
The function parses the XML file into a tree structure and iterates over all elements in the document. For each element, both the text content and the tail content are processed to:
- Replace the character sequence `&#13;` with a newline character for better readability.
- Decode any HTML entities (e.g. `&lt;`, `&amp;`) into their corresponding Unicode characters.

Once all textual content has been cleaned, the XML file is written back to disk using proper encoding and formatting. Any errors encountered during parsing or writing are logged and re-raised to ensure pipeline-level error visibility.

### Libraries Used
- **lxml.etree**: Used to parse, traverse, and write XML documents.
- **html**: Used to decode HTML entities into readable Unicode characters.
