from os.path import join
from lxml import etree
import pandas as pd


ELEMENTS_TO_REMOVE = ["ResponsableScientifique", "ContactSupplementaire"] 
FRESH_NAMESPACE_URI = "urn:fresh-enrichment:v1"

def update_contacts(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Updates contacts in the XML file:
      1. Removes existing contact-related elements listed in ELEMENTS_TO_REMOVE.
      2. Adds new contacts from the given Excel file (filtered by ID Fiche).
    
    Args:
        xml_file: The name of the XML file to modify.
        input_folder: Folder containing the XML file.
        output_folder: Folder to write the updated XML file.
        context (optional): Shared context object containing changelog, logger, etc.
    
    Returns:
        Path to the updated XML file.
    """
    logger = context.get_logger() if context else None
    try:
        if logger:
            logger.info("Processing XML file to update contacts: %s", xml_file)

        input_path = join(input_folder, xml_file)

        # Parse XML
        tree = etree.parse(input_path)
        root = tree.getroot()

        task_name = "update_contacts"
        changelog = context.get_changelog(xml_file) if context else None

        # --- STEP 1: remove existing contacts ---
        logged_values = set()

        def _remove_recursively(parent):
            for child in list(parent):
                tag_without_ns = etree.QName(child).localname
                if tag_without_ns in ELEMENTS_TO_REMOVE:
                    # Log leaf text values once
                    for leaf in child.iter():
                        if len(leaf) == 0 and leaf.text and leaf.text.strip():
                            value = leaf.text.strip()
                            if value not in logged_values:
                                logged_values.add(value)
                                if changelog:
                                    changelog.log_delete(task_name, field=tag_without_ns, old_value=value)
                    parent.remove(child)
                else:
                    _remove_recursively(child)

        _remove_recursively(root)

        # Get Excel mapping path
        tables_folder = context.get_conversion_tables_folder()
        excel_path = join(tables_folder, 'ContatsID_VF.xlsx')
        # --- STEP 2: load Excel and filter rows ---
        df = pd.read_excel(excel_path, dtype=str).fillna("")
        file_id = xml_file.split("_")[0]  # prima parte del nome file
        df_file = df[df["ID Fiche"].astype(str) == file_id]

        if logger:
            logger.info("Found %d contacts in Excel for file_id=%s", len(df_file), file_id)

        # --- STEP 3: add new contacts ---
        nsmap = root.nsmap.copy()
        if "fresh" not in nsmap:
            nsmap["fresh"] = FRESH_NAMESPACE_URI

        for _, row in df_file.iterrows():
            role = row["Role"].strip()
            name = row["Prénom Nom"].strip()
            mail = row["Mail"].strip() 
            orcid = row.get("OrcidFinal", "").strip()
            idref = row.get("IdRefFinal", "").strip()

            # === PrimaryInvestigator / Contributor ===
            if role == "PI":
                contact_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}PrimaryInvestigator", nsmap=nsmap)
                name_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}PIName")
                name_elem.text = name
                contact_elem.append(name_elem)
            else:
                contact_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}Contributor", nsmap=nsmap)
                name_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}ContributorName")
                name_elem.text = name
                contact_elem.append(name_elem)

            # Add PersonPID(s)
            if orcid:
                pid_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}PersonPID")
                uri_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}URI")
                uri_elem.text = orcid
                schema_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}PIDSchema")
                schema_elem.text = "ORCID"
                pid_elem.extend([uri_elem, schema_elem])
                contact_elem.append(pid_elem)

            if idref:
                pid_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}PersonPID")
                uri_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}URI")
                uri_elem.text = idref
                schema_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}PIDSchema")
                schema_elem.text = "IdRef"
                pid_elem.extend([uri_elem, schema_elem])
                contact_elem.append(pid_elem)

            # Append new contact to root
            root.append(contact_elem)

            if changelog:
                for leaf in contact_elem.iter():
                    if len(leaf) == 0 and leaf.text and leaf.text.strip():
                        changelog.log_add(task_name, field=etree.QName(leaf).localname, new_value=leaf.text.strip())

            # === ContactPoint (same level, if mail exists) ===
            if mail:
                cp_elem = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}ContactPoint", nsmap=nsmap)
                cp_name = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}ContactName")
                cp_name.text = name
                cp_mail = etree.Element(f"{{{FRESH_NAMESPACE_URI}}}EMail")
                cp_mail.text = mail
                cp_elem.extend([cp_name, cp_mail])
                root.append(cp_elem)

                if changelog:
                    for leaf in cp_elem.iter():
                        if len(leaf) == 0 and leaf.text and leaf.text.strip():
                            changelog.log_add(task_name, field=etree.QName(leaf).localname, new_value=leaf.text.strip())

        # --- STEP 4: write output ---
        output_path = join(output_folder, xml_file)
        tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)

        if logger:
            logger.info("Successfully wrote updated XML file: %s", output_path)

        return output_path

    except Exception as e:
        if logger:
            logger.error("Error while processing file %s: %s", xml_file, e)
        raise
