from .correct_special_characters import correct_special_characters
from .correct_special_characters_optional import correct_special_characters_optional
from .get_xml_files import get_xml_files
from .process_collection_dates import process_collection_dates
from .add_fresh_enrichment_namespace import add_fresh_enrichment_namespace
from .add_fresh_identifier import add_fresh_identifier
from .process_inclusion_criteria import process_inclusion_criteria
from .dispatch_data_access import dispatch_data_access
from .split_fr_en import split_fr_en


# Define __all__ to specify the public API of the tasks module
__all__ = [
    "correct_special_characters",
    "correct_special_characters_optional",
    "get_xml_files",
    "process_collection_dates",
    "add_fresh_enrichment_namespace",
    "add_fresh_identifier",
    "process_inclusion_criteria",
    "dispatch_data_access",
    "split_fr_en"

]