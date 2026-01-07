# FieldTransformer

## Overview
`FieldTransformer` applies XML transformations to a single file using a combination of:

- Excel lookup tables  
- A corresponding JSON configuration file  

It supports two operational modes:

1. **`by_id` (default)**  
   Transformations are applied based on a unique file identifier (e.g., file name), matching the corresponding row in Excel.

2. **`general`**  
   Transformations are applied row-by-row across the entire Excel table, matching values globally in the XML without requiring a specific file ID.

All changes are tracked using a provided **`Changelog`** instance.

---

## Attributes

| Attribute          | Type           | Description |
|-------------------|----------------|-------------|
| `task_name`       | `str`          | Task name used for changelog grouping. |
| `excel_filename`  | `str`          | Excel mapping table filename. |
| `excel_path`      | `str`          | Full path to the Excel file (`files/conversion-tables`). |
| `file_id`         | `str`          | Unique identifier for the current XML file. |
| `changelog`       | `Changelog`    | Changelog instance to record all modifications. |
| `config_path`     | `str`          | Path to the JSON configuration file. |
| `config`          | `dict`         | Parsed JSON configuration. |
| `df`              | `pd.DataFrame` | Loaded Excel data as a DataFrame. |
| `row`             | `pd.Series`    | Matched row for the current file (used in `by_id` mode). |
| `mode`            | `str`          | Operation mode: `"by_id"` or `"general"`. |
| `_replace_set_logged` | `set`       | Internal set to track logging of `replace_set` operations. |

---

## Initialization & Loading

### `__init__(excel_path: str, file_id: str, task_name: str, changelog: Changelog)`
Initializes the transformer, loads the configuration and Excel table, and matches the row if in `by_id` mode.

### `_resolve_config_path() -> str`
Returns the path to the JSON configuration file associated with the Excel table.

### `_load_config()`
Loads the JSON config and validates required fields.  
- Raises `FileNotFoundError` if config does not exist.  
- Raises `ValueError` if JSON is invalid or required fields are missing.

### `_load_excel()`
Loads the Excel table as a pandas DataFrame and validates required columns.

### `_validate_excel_columns()`
Checks that all columns referenced in operations exist in the Excel table.  
- Raises `ValueError` if any expected column is missing.

### `_match_row()`
Selects the row in Excel matching `file_id` (used in `by_id` mode).

---

## Utility Functions

### `_sanitize_for_xml(value) -> str`
Cleans a value to make it safe for XML output:
- Removes invalid characters
- Decodes newline/tab artifacts
- Escapes HTML entities
- Normalizes whitespace

### `_normalize_xpath(xpath) -> str`
Converts shorthand XPath to a fully-qualified one, ensuring it starts with `/`, `//`, or `.`.

### `_is_significant(value) -> bool`
Returns `True` if a string contains meaningful content (non-whitespace).

### `_extract_value_nodes(node) -> List[etree._Element]`
Returns all `<value>` sub-elements, or the node itself if `<value>` does not exist.

---

## Applying Transformations

### `apply_transformations(tree: etree._ElementTree) -> etree._ElementTree`
Applies all operations defined in the JSON configuration to the XML tree.  
- In `by_id` mode: applies only to the matched row.  
- In `general` mode: applies to all rows in the Excel table.

### `_apply_operation(op: dict, root: etree._Element, row: pd.Series)`
Dispatches an operation to the appropriate handler based on `op["type"]`:
- `"update"` → `_apply_update`
- `"add"` → `_apply_add`
- `"delete"` → `_apply_delete`
- `"replace_set"` → `_apply_replace_set`

---

## Supported Operation Types

### `_apply_update(op, root, row)`
Updates existing values in the XML:
- If `from.col` exists → replaces matching values.
- Otherwise → replaces the first value found at `from.xpath`.

### `_apply_add(op, root, row)`
Adds a new element to the XML tree at the target XPath with the specified value.

### `_apply_delete(op, root, row)`
Deletes elements matching the XPath:
- If `from.col` is defined → deletes only matching values.
- Otherwise → deletes all child `<value>` elements.

### `_apply_replace_set(op, root, row)`
Replaces all `<value>` elements at the target XPath with values mapped from Excel.  
- Designed for `general` mode.
- Logs each new value only once per operation.

---

## Summary

`FieldTransformer` provides a flexible and fully configurable framework to:

- Apply XML transformations based on Excel mappings and JSON configurations.  
- Normalize and sanitize values for XML compatibility.  
- Add, update, delete, or replace sets of values in an XML file.  
- Track every change through a `Changelog`.

It supports both **file-specific** and **global** transformations and ensures safe handling of multiple `<value>` elements, Unicode normalization, and HTML entity decoding.


## Config file example

```json
{
  "mode": "by_id",
  "file_id_column": "ID",
  "operations": [
    {
      "type": "update",
      "enabled": true,
      "from": {
        "xpath": "//Study/Title",
        "col": "OldTitle"
      },
      "to": {
        "xpath": "//Study/Title",
        "col": "NewTitle"
      }
    },
    {
      "type": "add",
      "enabled": true,
      "from": {},
      "to": {
        "xpath": "//Study/Keywords",
        "col": "AdditionalKeyword",
        "is_fresh": true
      }
    },
    {
      "type": "delete",
      "enabled": true,
      "from": {
        "xpath": "//Study/Notes/Note",
        "col": "NoteToDelete"
      },
      "to": {}
    },
    {
      "type": "replace_set",
      "enabled": true,
      "from": {
        "xpath": "//Study/Subjects/Subject",
        "col": "OldSubject"
      },
      "to": {
        "xpath": "//Study/Subjects/Subject",
        "col": "NewSubject"
      }
    }
  ]
}
```

### Explanation:

- `"mode": "by_id"` → transformations are applied per file, using the `ID` column.  
- `"file_id_column": "ID"` → column in Excel used to match the file.  
- `"operations"` → list of transformations:

1. **Update**  
   Replace values at `//Study/Title` from `OldTitle` → `NewTitle`.

2. **Add**  
   Add new `<value>` elements to `//Study/Keywords` using `AdditionalKeyword`.

3. **Delete**  
   Delete `<Note>` elements whose text matches `NoteToDelete`.

4. **Replace_set**  
   Replace all `<Subject>` elements at the target XPath with mapped values from Excel (`OldSubject` → `NewSubject`).

---

