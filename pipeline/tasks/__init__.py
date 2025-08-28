from .correct_special_characters import correct_special_characters
from .correct_special_characters_optional import correct_special_characters_optional
from .get_xml_files import get_xml_files
from .process_collection_dates import process_collection_dates
from .add_fresh_enrichment_namespace import add_fresh_enrichment_namespace
from .add_fresh_identifier import add_fresh_identifier
from .process_inclusion_criteria import process_inclusion_criteria
from .dispatch_data_access import dispatch_data_access
from .update_regions import update_regions
from .align_health_determinants import align_health_determinants
from .align_biobank_content import align_biobank_content
from .align_data_types import align_data_types
from .align_health_specs import align_health_specs
from .add_collection_mode_categories import add_collection_mode_categories
from .update_recruitment_sources import update_recruitment_sources


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
    "update_regions",
    "align_health_determinants",
    "align_biobank_content",
    "align_data_types",
    "align_health_specs",
    "add_collection_mode_categories",
    "update_recruitment_sources",
    "split_fr_en"

]