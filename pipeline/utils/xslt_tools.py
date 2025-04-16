import logging
from saxonche import PySaxonProcessor

logger = logging.getLogger(__name__)

def execute_xsl_transformation(xml_file, xsl_file):
    try:
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xml_input = proc.parse_xml(xml_file_name=xml_file)
            xslt_exec = xsltproc.compile_stylesheet(stylesheet_file=xsl_file)
            xml_output = xslt_exec.transform_to_string(xdm_node=xml_input)
        return xml_output
    except Exception as e:
        logger.error(f"Errore nella trasformazione XSLT: {e}")
        raise