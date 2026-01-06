## add_related_documents

### About
This task enriches the XML file by adding `<RelatedDocument>` elements based on external reference data stored in an Excel file. Only the direct links to external resources or publication are object of this task. The docx or PDF files stored in the PEF database could not be parsed in the actual solution. Each related document may include a title/description and a URL.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to be processed.
- **input_folder** (`str`): Path to the folder containing the input XML file.
- **output_folder** (`str`): Path to the folder where the updated XML file will be saved.
- **context** (`optional`): Pipeline context providing access to the changelog and to shared configuration such as the folder containing conversion tables.

### External Files
- **20251028-liste-autres-liens.xlsx**: Excel file containing related document metadata.  
  It must include at least the following columns:
  - `ID`: Identifier used to match rows to the XML document ID.
  - `Description`: Human-readable title or description of the related document.
  - `url`: Link to the related document.

### Output Arguments
- **output_file_path** (`str`): Full path to the updated XML file containing the added `<RelatedDocument>` elements.

### How It Works
The function parses the input XML file and extracts its identifier from the `<ID>` element. It then loads an Excel table containing related document information and filters rows matching the XML identifier.

For each matching row, a new `<RelatedDocument>` element is created and appended to the XML root, containing:
- `<DocumentTitle>` populated from the Excel `Description` column
- `<DocumentLink>` populated from the Excel `url` column

Each addition can be optionally recorded in the pipeline changelog for traceability. Once all related documents are processed, the updated XML file is written to the output folder.

### Libraries Used
- **lxml.etree**: Used to parse, modify, and write XML documents.
- **pandas**: Used to read and filter the Excel file containing related document metadata.
