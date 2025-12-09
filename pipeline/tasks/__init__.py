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
from .update_population_types import update_population_types
from .add_rare_diseases import add_rare_diseases
from .add_nct_ids import add_nct_identifier
from .update_study_categories import update_study_categories
from .add_research_type import add_research_type
from .remove_duplicate_empty import remove_duplicate_empty
from .update_contacts import update_contacts
from .add_provenance import add_provenance
from .add_pathologies import add_pathologies
from .add_nations import add_nations
from .align_study_status import align_study_status
from .add_authorizing_agency import add_authorizing_agency
from .add_metadata_contributors import add_metadata_contributor
from .add_third_party_source import add_third_party_source
from .add_funding_type import add_funding_type
from .update_sponsor import update_sponsor
from .add_sampling_procedure import add_sampling_procedure
from .update_en_version import update_en_version
from .update_study_status import update_study_status
from .update_fundings import update_fundings
from .add_parent_category import add_parent_category
from .align_age import align_age
from .align_sex import align_sex
from .convert_icd_codes_to_uris import convert_icd_codes_to_uris
from .add_id_to_sex import add_id_to_sex
from .add_id_to_age import add_id_to_age
from .add_id_to_dataaccess import add_id_to_dataaccess
from .add_id_to_healthspecs import add_id_to_healthspecs


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
    "update_population_types",
    "add_rare_diseases",
    "add_nct_identifier",
    "update_study_categories",
    "add_research_type",
    "remove_duplicate_empty",
    "add_provenance",
    "update_contacts",
    "add_pathologies",
    "add_nations",
    "align_study_status",
    "add_authorizing_agency",
    "add_metadata_contributor",
    "add_third_party_source",
    "add_funding_type",
    "update_sponsor",
    "add_sampling_procedure",
    "update_en_version",
    "update_study_status",
    "update_fundings",
    "add_parent_category",
    "align_age",
    "align_sex",
    "convert_icd_codes_to_uris",
    "split_fr_en",
    "add_id_to_sex",
    "add_id_to_age",
    "add_id_to_dataaccess",
    "add_id_to_healthspecs",

]