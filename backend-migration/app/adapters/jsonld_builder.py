"""
Layer 3: Adapters
JSON-LD builder - implements JSONLDBuilder protocol
"""
from typing import Dict, Any
from app.core.entities.repository_metadata import RepositoryMetadata


class JSONLDBuilder:
    """
    Builds JSON-LD documents from RepositoryMetadata.
    Implements the JSONLDBuilder protocol from Layer 2.
    """
    
    def build_jsonld(self, metadata: RepositoryMetadata, schema: str, has_release: bool) -> Dict[str, Any]:
        """
        Build JSON-LD document from metadata.
        
        Args:
            metadata: RepositoryMetadata object
            schema: Schema type (maSMP or CODEMETA)
            has_release: Whether repository has releases
            
        Returns:
            JSON-LD document as dict
        """
        if schema == "maSMP":
            return self._build_masmp_jsonld(metadata, has_release)
        else:  # CODEMETA
            return self._build_codemeta_jsonld(metadata)
    
    def _build_masmp_jsonld(self, metadata: RepositoryMetadata, has_release: bool) -> Dict[str, Any]:
        """Build maSMP JSON-LD document"""
        return {
            "hasRelease": has_release,
            "maSMP:SoftwareSourceCode": self._build_software_source_code(metadata),
            "maSMP:SoftwareApplication": self._build_software_application(metadata)
        }
    
    def _build_codemeta_jsonld(self, metadata: RepositoryMetadata) -> Dict[str, Any]:
        """Build CODEMETA JSON-LD document"""
        jsonld = {
            "@context": [
                "http://schema.org/",
                {"codemeta": "https://w3id.org/codemeta/3.0"}
            ],
            "@type": "SoftwareSourceCode"
        }
        
        # Map metadata fields to JSON-LD
        self._add_fields_to_jsonld(jsonld, metadata, self._get_codemeta_fields())
        return jsonld
    
    def _build_software_source_code(self, metadata: RepositoryMetadata) -> Dict[str, Any]:
        """Build maSMP SoftwareSourceCode JSON-LD"""
        jsonld = {
            "@context": [
                "http://schema.org/",
                {"codemeta": "https://w3id.org/codemeta/3.0"},
                {"maSMP": "https://discovery.biothings.io/ns/maSMPProfiles/"}
            ],
            "@type": "maSMP:SoftwareSourceCode"
        }
        
        self._add_fields_to_jsonld(jsonld, metadata, self._get_masmp_source_code_fields())
        return jsonld
    
    def _build_software_application(self, metadata: RepositoryMetadata) -> Dict[str, Any]:
        """Build maSMP SoftwareApplication JSON-LD"""
        jsonld = {
            "@context": [
                "http://schema.org/",
                {"codemeta": "https://w3id.org/codemeta/3.0"},
                {"maSMP": "https://discovery.biothings.io/ns/maSMPProfiles/"}
            ],
            "@type": "maSMP:SoftwareApplication"
        }
        
        self._add_fields_to_jsonld(jsonld, metadata, self._get_masmp_application_fields())
        return jsonld
    
    def _add_fields_to_jsonld(self, jsonld: Dict[str, Any], metadata: RepositoryMetadata, allowed_fields: set):
        """Add metadata fields to JSON-LD document"""
        # Convert metadata to dict, excluding has_release (internal flag)
        metadata_dict = metadata.dict(exclude_none=True, exclude={"has_release"}, by_alias=True)
        
        for key, value in metadata_dict.items():
            # Map field names (e.g., codemeta_readme -> codemeta:readme)
            jsonld_key = key.replace("_", ":")
            if jsonld_key in allowed_fields or key in allowed_fields:
                # Skip empty lists
                if isinstance(value, list) and not value:
                    continue
                jsonld[jsonld_key] = value
    
    def _get_codemeta_fields(self) -> set:
        """Get allowed CODEMETA fields"""
        return {
            "name", "alternateName", "author", "version", "description", "citation",
            "codemeta:buildInstructions", "documentation", "softwareRequirements",
            "contributor", "license", "identifier", "dateCreated", "dateModified",
            "datePublished", "downloadUrl", "keywords", "codemeta:hasSourceCode",
            "releaseNotes", "codemeta:issueTracker", "programmingLanguage",
            "codemeta:developmentStatus", "codemeta:referencePublication",
            "codemeta:readme", "image", "logo", "applicationCategory", "discussionUrl"
        }
    
    def _get_masmp_source_code_fields(self) -> set:
        """Get allowed maSMP SoftwareSourceCode fields"""
        return {
            "codeRepository", "programmingLanguage", "version", "description", "name",
            "url", "maSMP:versionControlSystem", "hasSourceCode", "archivedAt",
            "author", "citation", "identifier", "keywords", "license",
            "codemeta:readme", "maSMP:intendedUse", "codeSampleType", "runtimePlatform",
            "conditionsOfAccess", "contributor", "copyrightHolder", "dateModified",
            "datePublished", "discussionUrl", "maintainer", "isAccessibleForFree",
            "codemeta:buildInstructions", "codemeta:issueTracker",
            "codemeta:referencePublication", "maSMP:developerDocumentation",
            "maSMP:learningResource", "maSMP:changelog", "maSMP:userDocumentation",
            "maSMP:deployInstructions", "maSMP:installInstructions", "maSMP:testInstructions"
        }
    
    def _get_masmp_application_fields(self) -> set:
        """Get allowed maSMP SoftwareApplication fields"""
        return {
            "description", "name", "url", "archivedAt", "author", "citation",
            "codemeta:readme", "maSMP:intendedUse", "releaseNotes", "softwareVersion",
            "keywords", "license", "identifier", "isAccessibleForFree",
            "maSMP:developerDocumentation", "maSMP:userDocumentation",
            "maSMP:learningResource", "codemeta:referencePublication",
            "codemeta:buildInstructions", "codemeta:issueTracker", "maSMP:changelog",
            "maSMP:deployInstructions", "maSMP:installInstructions",
            "maSMP:testInstructions", "memoryRequirements", "operatingSystem",
            "processorRequirements", "softwareRequirements", "storageRequirements",
            "conditionsOfAccess", "contributor", "copyrightHolder", "dateModified",
            "datePublished", "discussionUrl", "maintainer"
        }

