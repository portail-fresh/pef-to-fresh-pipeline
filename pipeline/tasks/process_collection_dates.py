import logging
from os.path import join
from lxml import etree
import dateutil.parser
from datetime import datetime

# Create a logger for this module
logger = logging.getLogger(__name__)

def process_collection_dates(xml_file: str, input_folder: str, output_folder: str):
    """
    Processes year elements in an XML file, converting them to a standard format and managing attributes based on specific conditions.

    This function performs the following steps:
    1. Parses the given XML file.
    2. Identifies and processes specific year-related elements.
    3. Converts recognized date formats into standardized four-digit years.
    4. Removes elements containing predefined phrases indicating an ongoing collection.
    5. Handles predefined mappings for unstructured date values.
    6. Saves the transformed XML file to the specified output folder.

    Args:
        xml_file (str): The name of the XML file to process.
        input_folder (str): The directory containing the XML file.
        output_folder (str): The directory where the processed XML file will be saved.

    Raises:
        ValueError: If an encountered date value cannot be parsed or mapped.
        Exception: For any unexpected errors during processing.
    """
    try:
        logger.info("Processing collection years in XML file: %s", xml_file)
        file_path = join(input_folder, xml_file)

        # Step 1: Parse the XML file
        tree = etree.parse(file_path)
        root = tree.getroot()

        YEAR_ELEMENTS = [
            "AnneePremierRecueilFR", "AnneePremierRecueilEN", 
            "AnneeDernierRecueilFR", "AnneeDernierRecueilEN"
        ]

        COLL_ONGOING_TOKENS = [
            'pas de date de fin', 'indéterminée', 'Etude ouverte longitudinale',
            'Indéterminé', 'Toujours actif', 'en cours',
            'ongoing', 'ouvert', 'undetermined', 'No completion date',
            'Open-longitudinal study', 'NA', 'Always active', 'Collection in progress', 'on-going', 'in progress'
        ]

        UNPARSED_DATES_DICT = {
            '2016-2017': '2017',
            '02/2015 dernière inclusion, 02/2017 dernier suivi': '2017',
            '0/5/2019': '2019',
            '20 juin 2020': '2020',
            '31 décembre 2013': '2013',
            'December 2014 (E4N-G1)': '2014',
            'December 2020 (E4N-G2)': '2020',
            'Mars 2012': '2012',
            '05/2012 (inclusion terminée)': '2012',
            '02/2015 last recruitment, 02/2017 last follow-up': '2017',
            'Octobre 2010': '2010',
            '2003 (élargissement de CEMARA)': '2003',
            'Mai 2012': '2012',
            'Avril 2012': '2012',
            'up to 2037': '2037',
            '2021 minimum': '2021',
            '1 janvier 2010': '2010',
            'Mars 2020': '2020',
            '12 juin 2020': '2020',
            'Février 2021': '2021',
            'Mai 2015': '2020',
            '2012 (pilote)': '2012',
            '05/2012 (inclusion completed)': '2012',
            '2003 (expansion of CEMARA [CEntres MAladies RAres (Rare Disease Centres)]': '2003',
            'Mars 2011': '2011',
            'Juillet 2012': '2012',
            '01/2016 (théorique)': '2016',
            'Décembre 2013': '2013',
            'up to 2036': '2036',
            'Juin 2020': '2020',
            '20 juin 2020 ': '2020',
            'Fevrier 2021': '2021',
            '01/2016 (hypothetical)': '2016',
            '07/2018 (théorique)': '2018',
            '07/2018 (hypothetical)': '2018'
        }

        def parse_year(date_text):
            try:
                parsed_date = dateutil.parser.parse(date_text, default=datetime(1970, 1, 1), fuzzy=False)
                return str(parsed_date.year)
            except ValueError:
                return None

        def contains_any_substring(target_string, substrings):
            return any(sub.lower() in target_string.lower() for sub in substrings)

        year_values = {}
        for element in YEAR_ELEMENTS:
            for el in root.xpath(f"//{element}"):
                if el.text is not None:
                    if contains_any_substring(el.text, COLL_ONGOING_TOKENS):
                        el.getparent().remove(el)
                        continue
                    
                    converted_year = parse_year(el.text)
                    if converted_year is None:
                        converted_year = UNPARSED_DATES_DICT.get(el.text, None)
                        if converted_year is None:
                            raise ValueError(f"Unrecognized date format: '{el.text}'. Unable to parse.")
                    
                    el.text = converted_year
                    year_values[element] = converted_year

        # Validate French and English dates match
        #if year_values.get("AnneePremierRecueilFR") and year_values.get("AnneePremierRecueilEN"):
        #    if year_values["AnneePremierRecueilFR"] != year_values["AnneePremierRecueilEN"]:
        #        raise Exception(f"Mismatch: AnneePremierRecueilFR ({year_values['AnneePremierRecueilFR']}) != AnneePremierRecueilEN ({year_values['AnneePremierRecueilEN']})")
        
        #if year_values.get("AnneeDernierRecueilFR") and year_values.get("AnneeDernierRecueilEN"):
        #    if year_values["AnneeDernierRecueilFR"] != year_values["AnneeDernierRecueilEN"]:
        #        raise Exception(f"Mismatch: AnneeDernierRecueilFR ({year_values['AnneeDernierRecueilFR']}) != AnneeDernierRecueilEN ({year_values['AnneeDernierRecueilEN']})")

        # Step 2: Save the updated XML file
        output_file_path = join(output_folder, xml_file)
        tree.write(output_file_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        logger.info("Successfully processed and saved XML file: %s", output_file_path)
    
    except ValueError as ve:
        logger.error("Date parsing error in file %s: %s", xml_file, ve)
        raise
    except Exception as e:
        logger.error("An unexpected error occurred while processing the file %s: %s", xml_file, e)
        raise

