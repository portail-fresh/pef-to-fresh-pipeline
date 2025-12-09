from pathlib import Path
from lxml import etree
import pandas as pd
from os.path import join
import unicodedata

# External, configurable variable used in the pipeline
VOCAB_EXCEL = "Age.xlsx"


def normalize_key(s: str) -> str:
    """
    Normalize a string to make text comparisons consistent and reliable.

    - Strips whitespace
    - Normalizes Unicode into NFC form
    - Converts to lowercase

    Args:
        s (str): Input string.

    Returns:
        str: Normalized string. Returns empty string if input is None.
    """
    if s is None:
        return ""
    s = s.strip()
    s = unicodedata.normalize("NFC", s)
    return s.lower()


def add_id_to_age(
    xml_file: str,
    input_folder: str,
    output_folder: str,
    context=None
):
    """
    Enriches <value> elements inside <TranchesAgeFR> and <TranchesAgeEN> tags by adding:
        - uri:  extracted from the Excel vocabulary
        - vocab: derived from the Excel column prefix "URI_<vocab>"

    This function is generic and works with ANY vocabulary Excel file
    structured as follows:

        URI_XYZ | label_fr | label_en

    The language columns may contain labels in French and English.
    The function matches textual labels from the XML with these
    normalized lookup tables and attaches the corresponding URI info.

    Args:
        xml_file (str): Name of the XML file to process.
        input_folder (str): Folder containing the original XML file.
        output_folder (str): Folder where the processed XML file will be saved.
        context: Optional pipeline context with logger and changelog utilities.

    Raises:
        ValueError: If vocabulary structure is invalid or if a label in XML
                    is missing from the Excel vocabulary.
    """
    try:
        # Retrieve optional logger and changelog utilities from the pipeline context
        logger = context.get_logger() if context else None
        changelog = context.get_changelog(xml_file) if context else None

        if logger:
            logger.info("Starting vocabulary enrichment for file: %s", xml_file)

        # Build input/output paths
        input_path = Path(input_folder) / xml_file
        output_path = Path(output_folder) / xml_file

        # Abort if XML file is missing
        if not input_path.exists():
            if logger:
                logger.error("Input XML file '%s' not found. Skipping.", input_path)
            return

        # Parse XML tree
        try:
            tree = etree.parse(str(input_path))
            root = tree.getroot()
        except etree.XMLSyntaxError as e:
            if logger:
                logger.error("Failed to parse '%s': %s", xml_file, e)
            return

        # -------- READ VOCABULARY FROM EXCEL --------
        tables_folder = context.get_vocabs_folder()
        excel_path = join(tables_folder, VOCAB_EXCEL)

        # Read Excel as strings and convert NaN → empty strings
        df = pd.read_excel(excel_path, dtype=str).fillna("")

        # Identify the unique "URI_*" vocabulary column (e.g. URI_MeSH)
        uri_columns = [c for c in df.columns if c.startswith("URI_")]
        if len(uri_columns) != 1:
            raise ValueError(
                f"Excel file '{VOCAB_EXCEL}' must contain exactly one column "
                f"starting with 'URI_'. Found: {uri_columns}"
            )

        uri_col = uri_columns[0]             # e.g. "URI_MeSH"
        vocab = uri_col.split("_", 1)[1]     # → "MeSH"

        # Build lookup dictionaries for FR and EN labels (normalized)
        fr_map = {}
        en_map = {}

        for _, row in df.iterrows():
            uri = row[uri_col].strip()
            label_fr = row["label_fr"].strip()
            label_en = row["label_en"].strip()

            # Add FR mapping
            if label_fr:
                fr_map[normalize_key(label_fr)] = (uri, vocab)

            # Add EN mapping
            if label_en:
                en_map[normalize_key(label_en)] = (uri, vocab)

        # -------- PROCESS XML AND ADD ATTRIBUTES --------
        target_tags = {
            "TranchesAgeFR": fr_map,
            "TranchesAgeEN": en_map,
        }

        # For <SexeFR> and <SexeEN>, enrich child <value> nodes
        for tag, mapping in target_tags.items():
            for parent in root.findall(f".//{tag}"):
                for val_el in parent.findall("value"):
                    raw_text = (val_el.text or "").strip()
                    key = normalize_key(raw_text)
                    
                    if not key: 
                        continue
                    
                    

                    # Check vocabulary consistency
                    if key not in mapping:
                        raise ValueError(
                            f"Value '{raw_text}' found in <{tag}> is not present in the vocabulary "
                            f"(XML: {xml_file}, Excel: {VOCAB_EXCEL})"
                        )

                    uri, vocab_name = mapping[key]
                    
                    if not uri:
                        continue

                    # Add attributes to the XML
                    val_el.set("uri", uri)
                    val_el.set("vocab", vocab_name)

                    # Log changes if a changelog is available
                    if changelog:
                        changelog.log_add(
                            task="add_vocabulary_uri",
                            field=tag,
                            new_value={
                                "value": raw_text,
                                "URI": uri,
                                "vocab": vocab_name,
                            },
                        )

        # -------- WRITE OUTPUT XML --------
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(
            str(output_path),
            pretty_print=True,
            encoding="utf-8",
            xml_declaration=True,
        )

        if logger:
            logger.info("Successfully added vocabulary URIs and saved: %s", output_path)

    except Exception as e:
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
