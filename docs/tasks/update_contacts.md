## update_contacts

### About
Updates contact information in an XML file. This task:

1. Removes existing contact-related elements such as `<ResponsableScientifique>` and `<ContactSupplementaire>`.
2. Adds new contacts from an Excel mapping file, filtered by the file ID.
3. Adds affiliation information, preferring `OrganismeNorm` with fallback to `LaboratoireNorm`.
4. Enriches contacts with persistent identifiers (ORCID, IdRef, RNSR, ROR, SIREN) when available.
5. Creates `<PrimaryInvestigator>` and `<Contributor>` elements within the FReSH namespace.
6. Optionally adds `<ContactPoint>` elements for contacts with email addresses.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to process.
- **input_folder** (`str`): Folder containing the original XML file.
- **output_folder** (`str`): Folder where the updated XML file will be saved.
- **context** (optional): Pipeline context providing logger and changelog utilities.

### External Files
- **`Contacts_arricchito_pids.xlsx`**: Excel file containing enriched contact information.  
  Columns used include:
  - `ID Fiche`: File identifier used to filter rows for the current XML.
  - `Role`: Role of the contact (`PI` for Primary Investigator, otherwise Contributor).
  - `Prénom`, `Nom`: Name and surname of the contact.
  - `Mail`: Email address.
  - `OrganismeNorm`, `LaboratoireNorm`: Affiliation information.
  - `OrcidFinal`, `IdRefFinal`, `RNSR`, `ROR`, `SIREN_DEF`: Persistent identifiers for people and organizations.  
  This file drives the creation of contact elements and their associated identifiers and affiliations in the XML.

### Output Arguments
- Saves the enriched XML file to the output folder.
- Logs all additions and deletions to the changelog if provided.

### How It Works
1. Parses the input XML using `lxml.etree`.
2. Recursively removes old contact elements defined in `ELEMENTS_TO_REMOVE`, logging deletions.
3. Loads the Excel mapping and filters rows by the current file ID.
4. For each contact row, creates either `<PrimaryInvestigator>` or `<Contributor>` elements, adds the name, email, affiliation, and persistent identifiers.
5. Adds `<ContactPoint>` elements for contacts with emails, including affiliation and identifiers.
6. Logs all new XML nodes to the changelog.
7. Writes the updated XML to the output folder with pretty formatting and XML declaration.

### Libraries Used
- **os.path.join**: Constructs platform-independent file paths.
- **lxml.etree**: Parses, manipulates, and writes XML documents.
- **pandas**: Reads Excel files and filters data.
