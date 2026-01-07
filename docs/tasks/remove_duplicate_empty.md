## remove_duplicate_empty

### About
Cleans an XML file by:
1. Removing **duplicate elements** (same tag and identical content, including their entire subtree).
2. Removing **completely empty elements** (no text, no attributes, no children).

This function is typically used as a final normalization/cleanup step in the pipeline to ensure the XML output is compact, consistent, and free of redundant or meaningless nodes.

### Input Arguments
- **xml_file** (`str`): Name of the XML file to clean.
- **input_folder** (`str`): Directory containing the source XML file.
- **output_folder** (`str`): Directory where the cleaned XML file will be written.
- **context** (optional): Pipeline context providing:
  - changelog (used to log deletions)

### How it works

#### Step 1 — Remove Duplicate Elements
- Traverses the XML tree recursively.
- For each parent element:
  - Computes a **canonical XML signature** (`c14n`) for each child element.
  - If two children have identical canonical representations (same tag, attributes, text, and subtree), only the first is kept.
- Duplicate elements are removed from the tree.
- Each deletion is logged to the changelog (if available).

**Definition of duplicate**  
Two elements are considered duplicates if their entire serialized XML subtree is identical.

#### Step 2 — Remove Empty Elements
- Traverses the XML tree bottom-up.
- An element is considered *empty* if:
  - it has no text (or only whitespace),
  - it has no attributes,
  - it has no child elements.
- Empty elements are removed recursively until no such elements remain.

### Output
- The cleaned XML file is written to the output folder with:
  - UTF-8 encoding
  - XML declaration
  - pretty printing enabled
- The function returns the output file path.

### Logging & Changelog
- Uses the module logger for progress and debug messages.
- When a changelog is available:
  - Duplicate removals are recorded using `log_delete`
  - Empty-element removals are **not** logged individually (by design, to avoid noise)

### Libraries Used
- **lxml.etree**
  - XML parsing
  - Canonical serialization (`c14n`)
  - Tree traversal and mutation


### Typical Use Case
- Final pipeline cleanup step after multiple enrichment/transformation tasks.
- Ensures:
  - no repeated metadata blocks,
  - no empty placeholders left by previous processing steps,
  - a stable and minimal XML structure.
