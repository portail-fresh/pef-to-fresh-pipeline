import logging
from os.path import join
from lxml import etree
import requests

logger = logging.getLogger(__name__)


def convert_icd_codes_to_uris(xml_file: str, input_folder: str, output_folder: str, context=None):
    """
    Converts ICD codes found in <Pathology> elements of an XML file into ICD-11 URIs
    using the WHO ICD API, then writes the updated XML file to the output folder.

    Args:
        xml_file (str): Name of the XML file to process.
        input_folder (str): Directory containing the input XML file.
        output_folder (str): Directory where the updated XML file will be saved.
        context (PipelineContext, optional): Shared context containing API credentials,
                                             changelog manager, and other runtime data.
    """
    try:
        logger.info("Processing ICD codes in XML file: %s", xml_file)
        file_path = join(input_folder, xml_file)
        tree = etree.parse(file_path)
        root = tree.getroot()

        # === Retrieve OAuth2 credentials from context ===
        CLIENT_ID = context.icd_client_id
        CLIENT_SECRET = context.icd_client_secret
        TOKEN_ENDPOINT = context.icd_token_endpoint

        # Static API parameters
        SCOPE = 'icdapi_access'
        GRANT_TYPE = 'client_credentials'
        API_URL = "https://id.who.int/icd/entity/autocode?searchText="

        uri_cache = {}

        # === OAuth2 Token Retrieval ===
        def get_token():
            """
            Requests an OAuth2 token using client credentials.
            """
            payload = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'scope': SCOPE,
                'grant_type': GRANT_TYPE
            }
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            r = requests.post(TOKEN_ENDPOINT, data=payload, verify=False)

            if r.status_code == 200:
                token = r.json().get('access_token')
                if token:
                    return token
                else:
                    raise Exception("Access token not found in response.")
            else:
                raise Exception(f"Oauth2 error: {r.status_code} - {r.text}")

        # === Use existing token if available, otherwise request a new one ===
        if hasattr(context, "icd_token") and context.icd_token:
            token = context.icd_token
            logger.info("Using existing ICD token from context.")
        else:
            logger.info("No valid token in context. Requesting new token...")
            token = get_token()
            context.icd_token = token  # Save token back to context
            logger.info("New ICD token stored in context.")

        # === ICD API lookup ===
        def get_icd11_uri(code):
            """
            Retrieves the ICD-11 URI for a given ICD code using the WHO API.

            Args:
                code (str): ICD code to be converted.

            Returns:
                str or None: Corresponding ICD-11 URI, or None if not found.
            """
            if code in uri_cache:
                return uri_cache[code]

            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json',
                'Accept-Language': 'en',
                'API-Version': 'v2'
            }
            response = requests.get(API_URL + code, headers=headers, verify=False)

            if response.status_code == 200:
                data = response.json()
                uri = data.get("foundationURI")
                if uri:
                    uri_cache[code] = uri
                    return uri
                else:
                    logger.warning(f"No ICD-11 URI found for code {code}")
                    return None
            else:
                logger.warning(f"API error for code {code}: {response.status_code}")
                return None

        # === XML processing ===
        nsmap = {'fresh': root.nsmap.get('fresh', '')}

        task_name = "convert_icd_codes_to_uris"
        changelog = context.get_changelog(xml_file) if context else None

        for elem in root.xpath('.//fresh:Pathology', namespaces=nsmap):
            code = elem.text.strip() if elem.text else None
            if not code:
                continue


            uri = get_icd11_uri(code)
            if uri:
                if changelog:
                    changelog.log_update(task_name, field="Pathology", old_value=code, new_value=uri)
                elem.text = uri
                

        # === Save updated XML ===
        output_file_path = join(output_folder, xml_file)
        tree.write(output_file_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        logger.info("Successfully processed and saved XML file: %s", output_file_path)

    except Exception as e:
        logger.error("Error while processing file %s: %s", xml_file, e)
        raise
