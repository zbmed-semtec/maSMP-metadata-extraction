"""Extract authors from CITATION.cff into step state."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.cff_parse import CffParsePlugin
from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractCitationAuthorsStep(ExtractionPlugin):
    """Extract top-level CFF authors without mutating metadata."""

    name = "citation.extract_authors"
    extracts = {"https://schema.org/author"} # this plugin is not called directly, but is a sub-plugin to 'extract_author'
    platforms = {"gitlab", "github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        cpp : CffParsePlugin= self.plugin_manager.get('cff-parse-plugin')
        cpp.ensure_cff_yaml_loaded(context, state)
        if not state.data.get("valid"):
            return state
        extracted_authors = []
        for author in state.data["cff_data"].get("authors") or []:
            person = {
                "@type": "Person",
                "familyName": author.get("family-names"),
                "givenName": author.get("given-names"),
            }
            if "orcid" in author:
                person["@id"] = author["orcid"]
            extracted_authors.append(person)
        state.data["extracted_citation_authors"] = extracted_authors
        return state




