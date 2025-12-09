from pathlib import Path
from lxml import etree
import pandas as pd
from os.path import join
import unicodedata

# External, configurable variable used in the pipeline
VOCAB_EXCEL = "HealthTheme.xlsx"


def normalize_key(s: str) -> str:
    if s is None:
        return ""
    s = s.strip()
    s = unicodedata.normalize("NFC", s)
    return s.lower()


def add_id_to_healthspecs(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Enrich <DomainesDePathologiesFR> and <DomainesDePathologiesEN> elements by creating
    <concept uri="..." vocab="..."> sub-elements for each vocabulary URI.

    Handles multiple URIs per term (separated by "|") in the Excel file.
    Sets `vocab` to the actual vocabulary name (e.g., "MeSH") instead of the column name.
    """
    try:
        logger = context.get_logger() if context else None
        changelog = context.get_changelog(xml_file) if context else None

        if logger:
            logger.info("Starting enrichment of DomainesDePathologies for file: %s", xml_file)

        # Paths
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

        # Identify URI columns and map them to vocabulary names
        uri_cols = [c for c in df.columns if c.startswith("URI_")]
        if not uri_cols:
            raise ValueError(f"No URI columns found in {VOCAB_EXCEL}")

        # Build lookup tables for FR and EN
        fr_map = {}
        en_map = {}

        for _, row in df.iterrows():
            uris_list = {}
            for col in uri_cols:
                values = [u.strip() for u in row[col].split("|") if u.strip()]
                if values:
                    vocab_name = col.split("_", 1)[1]  # "URI_MeSH" → "MeSH"
                    uris_list[vocab_name] = values

            label_fr = row.get("label_fr", "").strip()
            label_en = row.get("label_en", "").strip()

            if label_fr and uris_list:
                fr_map[normalize_key(label_fr)] = uris_list
            if label_en and uris_list:
                en_map[normalize_key(label_en)] = uris_list

        # -------- PROCESS XML --------
        target_tags = {
            "DomainesDePathologiesFR": fr_map,
            "DomainesDePathologiesEN": en_map,
        }

        for tag, mapping in target_tags.items():
            for parent_el in root.findall(f".//{tag}"):
                for val_el in parent_el.findall("value"):
                    raw_text = (val_el.text or "").strip()
                    key = normalize_key(raw_text)

                    if not key or key not in mapping:
                        continue  # skip empty or unknown terms

                    uris_list = mapping[key]

                    # Create <concept> sub-elements
                    for vocab_name, uris in uris_list.items():
                        for uri in uris:
                            concept_el = etree.SubElement(val_el, "concept")
                            concept_el.set("uri", uri)
                            concept_el.set("vocab", vocab_name)

                            if changelog:
                                changelog.log_add(
                                    task="add_vocabulary_concept",
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
            logger.info("Successfully enriched DomainesDePathologies: %s", output_path)

    except Exception as e:
        if logger:
            logger.error("Unexpected error while processing '%s': %s", xml_file, e)
        raise
