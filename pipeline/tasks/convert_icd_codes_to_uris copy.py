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
        API_CODEINFO = "https://id.who.int/icd/release/11/2025-01/mms/codeinfo/"
        API_ENTITY = "https://id.who.int/icd/release/11/2025-01/mms/"               

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
        def get_icd11_uri(code, token):
            """
            Recupera la URI ICD-11 relativa a un codice ICD effettuando due chiamate ai servizi WHO:
            1) Ottiene lo stemId dal servizio codeinfo.
            2) Usa lo stemId per interrogare l'entità e ricavare l'URI dal campo 'source'.

            Args:
                code (str): Codice ICD da convertire.
                token (str): Token Bearer per l'autenticazione.

            Returns:
                str or None: URI ICD-11 corrispondente, oppure None se non trovata.
            """
            
            def pad_if_1_to_9(s: str) -> str:
                if s.isdigit() and 1 <= int(s) <= 9:
                    return s.zfill(2)
                return s
            
            code=pad_if_1_to_9(code)
            
            # Controllo cache
            if code in uri_cache:
                return uri_cache[code]

            # Header con autenticazione
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Accept-Language": "en",
                "API-Version": "v2"
            }

            # --- 1. Chiamata: recupero dello stemId ---
            url_info = f"{API_CODEINFO}{code}?flexiblemode=true"

            try:
                resp_info = requests.get(url_info, headers=headers, verify=False, timeout=10)
            except Exception as e:
                logger.warning(f"Errore nella richiesta per il codice {code}: {e}")
                return None

            if resp_info.status_code != 200:
                logger.warning(f"Errore codeinfo per {code}: {resp_info.status_code}")
                return None

            data_info = resp_info.json()
            api_code = data_info.get("code")
            if api_code!=code:
                print(data_info)
                print(code, api_code)
                raise Exception
                return None
            
            stem_id_full = data_info.get("stemId")
            if not stem_id_full or "/mms/" not in stem_id_full:
                logger.warning(f"stemId mancante o non valido per il codice {code}")
                return None

            # Estrarre lo stemId dopo /mms/
            stem_id = stem_id_full.split("/mms/")[-1].split("/")[0]

            # --- 2. Chiamata: recupero dell'URI dal campo 'source' ---
            url_entity = f"{API_ENTITY}{stem_id}"

            try:
                resp_entity = requests.get(url_entity, headers=headers, verify=False, timeout=10)
            except Exception as e:
                logger.warning(f"Errore nella richiesta entità per ID {stem_id}: {e}")
                return None

            if resp_entity.status_code != 200:
                logger.warning(f"Errore entità ICD per {stem_id}: {resp_entity.status_code}")
                return None

            data_entity = resp_entity.json()

            uri = data_entity.get("source")
            icd_title = data_entity.get("title")
            if not icd_title:
                print(data_entity)
                raise Exception

            if not uri:
                logger.warning(f"Nessun campo 'source' trovato per lo stemId {stem_id}")
                return None

            # Salvo in cache
            uri_cache[code] = uri
            return uri

        # === XML processing ===
        nsmap = {'fresh': root.nsmap.get('fresh', '')}

        task_name = "convert_icd_codes_to_uris"
        changelog = context.get_changelog(xml_file) if context else None

        for elem in root.xpath('.//fresh:Pathology', namespaces=nsmap):
            code = elem.text.strip() if elem.text else None
            if not code:
                continue


            uri = get_icd11_uri(code, token)
            print("uri:",uri)
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
