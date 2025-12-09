from pathlib import Path
from lxml import etree
import pandas as pd
from os.path import join
import unicodedata

# External, configurable variable used in the pipeline
VOCAB_EXCEL = "IndividualDataAccess.xlsx"
FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"


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


def add_id_to_dataaccess(
    xml_file: str,
    input_folder: str,
    output_folder: str,
    context=None
):
    """
    Enriches <IndividualDataAccessFR> and <IndividualDataAccessEN> elements
    by adding:
        - uri:  extracted from the Excel vocabulary
        - vocab: derived from the Excel column prefix "URI_<vocab>"

    Uses the FRESH namespace and skips elements that are empty or have no URI.

    Args:
        xml_file (str): Name of the XML file to process.
        input_folder (str): Folder containing the original XML file.
        output_folder (str): Folder where the processed XML file will be saved.
        context: Optional pipeline context with logger and changelog utilities.

    Raises:
        ValueError: If vocabulary structure is invalid.
    """
    try:
        # Retrieve optional logger and changelog
        logger = context.get_logger() if context else None
        changelog = context.get_changelog(xml_file) if context else None

        if logger:
            logger.info("Starting vocabulary enrichment for file: %s", xml_file)

        # Input/output paths
        input_path = Path(input_folder) / xml_file
        output_path = Path(output_folder) / xml_file

        if not input_path.exists():
            if logger:
                logger.error("Input XML file '%s' not found. Skipping.", input_path)
            return

        # Parse XML
        try:
            tree = etree.parse(str(input_path))
            root = tree.getroot()
        except etree.XMLSyntaxError as e:
            if logger:
                logger.error("Failed to parse '%s': %s", xml_file, e)
            return

        # -------- READ VOCABULARY --------
        tables_folder = context.get_vocabs_folder()
        excel_path = join(tables_folder, VOCAB_EXCEL)

        df = pd.read_excel(excel_path, dtype=str).fillna("")

        # Identify URI column
        uri_columns = [c for c in df.columns if c.startswith("URI_")]
        if len(uri_columns) != 1:
            raise ValueError(
                f"Excel file '{VOCAB_EXCEL}' must contain exactly one column "
                f"starting with 'URI_'. Found: {uri_columns}"
            )

        uri_col = uri_columns[0]
        vocab = uri_col.split("_", 1)[1]

        fr_map = {}
        en_map = {}
        for _, row in df.iterrows():
            uri = row[uri_col].strip()
            label_fr = row.get("label_fr", "").strip()
            label_en = row.get("label_en", "").strip()

            if label_fr and uri:
                fr_map[normalize_key(label_fr)] = (uri, vocab)
            if label_en and uri:
                en_map[normalize_key(label_en)] = (uri, vocab)

        # -------- PROCESS XML WITH FRESH NAMESPACE --------
        ns = {"fresh": FRESH_NAMESPACE_URI}

        target_tags = {
            "IndividualDataAccessFR": fr_map,
            "IndividualDataAccessEN": en_map,
        }

        for tag, mapping in target_tags.items():
            for el in root.findall(f".//fresh:{tag}", namespaces=ns):
                raw_text = (el.text or "").strip()
                key = normalize_key(raw_text)

                if not key:
                    continue  # skip empty elements

                if key not in mapping:
                    continue  # skip if no URI exists for this label

                uri, vocab_name = mapping[key]

                # Add attributes
                el.set("uri", uri)
                el.set("vocab", vocab_name)

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

        # -------- WRITE OUTPUT --------
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(
            str(output_path),
            pretty_print=True,
            encoding="utf-8",
            xml_declaration=True,
        )

        if logger:
            logger.info("Successfully enriched IndividualDataAccess elements: %s", output_path)

    except Exception as e:
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
