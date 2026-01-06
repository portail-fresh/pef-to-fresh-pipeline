## correct_special_characters

### About
This task cleans and normalizes an XML file by correcting invalid or problematic characters that may prevent proper XML parsing. Its main goal is to ensure the XML is well-formed and compliant with XML standards before being processed further in the pipeline.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the corrected XML file will be saved.

### Output Arguments
- **output_file_path** (`str`): Full path to the corrected XML file written to the output folder.

### How It Works
The function reads the XML file in binary mode and performs a series of byte-level replacements to fix common issues:
- Replaces all occurrences of the `&` character with the valid XML entity `&amp;`.
- Removes invalid control characters such as `\x01` and `\x02`.

After cleaning the content, the function attempts to parse the resulting XML string using an XML parser to ensure that it is well-formed. If parsing succeeds, the corrected XML is written to the output folder with proper encoding, XML declaration, and formatting. Any errors encountered during the process are logged and re-raised to allow pipeline-level error tracking.

### Libraries Used
- **lxml.etree**: Used to parse, validate, and write XML content.

