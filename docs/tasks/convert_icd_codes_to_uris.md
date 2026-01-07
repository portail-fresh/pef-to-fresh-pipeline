## convert_icd_codes_to_uris

### About
Enriches pathology information in the XML by converting ICD codes into official ICD-11 URIs.  
For each pathology code found in the XML, the function queries the WHO ICD-11 API to retrieve:
- the canonical ICD-11 URI
- the official English and French titles of the corresponding entity

The XML is then updated so that pathology entries reference stable, resolvable identifiers instead of raw codes.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Directory containing the source XML file.
- **output_folder** (`str`): Directory where the enriched XML file will be written.
- **context** (optional): Pipeline context providing:
  - logger
  - changelog
  - ICD API credentials (client id, client secret, token endpoint)
  - cached OAuth token (if already retrieved)

### External Files & Services
- **WHO ICD-11 API**  
  Used to:
  - resolve ICD codes to ICD-11 entities
  - retrieve the canonical ICD-11 URI
  - retrieve English and French titles for each entity  

  The API is accessed using OAuth2 *client credentials* flow, with credentials provided by the pipeline context.

### XML Elements Processed
- **`fresh:Pathology`**

For each `fresh:Pathology` element:
- The element text is expected to contain an ICD code.
- The text is replaced with the corresponding ICD-11 URI.
- Two optional attributes may be added:
  - `en`: English title of the ICD-11 entity
  - `fr`: French title of the ICD-11 entity

### Output
- The XML file is always written to the output folder.
- Only pathology elements with resolvable ICD-11 mappings are modified.
- Unresolvable or invalid codes are silently skipped.
- All successful updates are logged in the changelog when available.

### How It Works
1. Parses the input XML document.
2. Retrieves OAuth2 credentials and access token (reusing a cached token if available).
3. Scans the XML for `fresh:Pathology` elements.
4. For each ICD code found:
   - Normalizes the code when needed.
   - Queries the ICD-11 API to retrieve the corresponding entity (URI and stem ID).
   - Queries the API again to retrieve English and French titles.
5. Replaces the element text with the ICD-11 URI.
6. Adds language-specific titles as attributes.
7. Logs each successful conversion to the changelog.
8. Writes the enriched XML document to the output folder.

### Libraries Used
- **lxml.etree**: Used to parse, traverse, update, and write XML documents.
- **requests**: Used to interact with the WHO ICD-11 REST APIs over HTTP.
