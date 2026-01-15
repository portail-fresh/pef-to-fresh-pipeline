# get_xml_files

Retrieves a list of XML files from a specified folder, excluding files whose IDs are listed in a separate Excel exclusion file.

---

## Input arguments

| Parameter | Type | Description |
|-----------|------|-------------|
| `folder` | `str` | Path to the folder containing XML files. |
| `context` | `PipelineContext` | Pipeline context providing logging and other shared resources. |

---

## Outputs

`list` – A list of XML file names in the folder, after removing files whose IDs appear in the exclusion list.

---

## Raises

- `FileNotFoundError` – If the folder or the Excel exclusion file cannot be found.  
- `Exception` – For other unexpected errors during file retrieval or Excel processing.

---

## How it works

1. Reads the Excel file `public/utility-files/id-fiches-exclus-fresh.xlsx` to obtain a list of IDs to exclude.
2. Lists all files in the specified folder.
3. Filters files to include only:
   - Files ending with `.xml`.
   - Files whose leading ID (before `_`) is **not** in the exclusion list.
4. Logs the number of XML files retrieved after filtering.

---

