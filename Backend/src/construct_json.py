from .constants import CODEMETA, maSMP_SoftwareSourceCode, maSMP_SoftwareApplication, to_be_removed

def construct_json(data, schema):
    """Construct a JSON-LD document from extracted data and a schema."""

    # Define schema-specific types and properties
    schema_map = {
        "CODEMETA": {
            "type": "SoftwareSourceCode",
            "properties": CODEMETA
        },
        "maSMP:SoftwareSourceCode": {
            "type": "maSMP:SoftwareSourceCode",
            "properties": maSMP_SoftwareSourceCode
        },
        "maSMP:SoftwareApplication": {
            "type": "maSMP:SoftwareApplication",
            "properties": maSMP_SoftwareApplication
        }
    }

    def create_jsonld(schema_key):
        """Helper function to create a JSON-LD document for a specific schema."""
        # Initialize the common JSON-LD document context
        jsonld_document = {
            "@context": [
                "http://schema.org/",
                {"codemeta": "https://w3id.org/codemeta/3.0"}
            ],
            "@type": schema_map[schema_key]["type"]
        }

        # Add maSMP context if it's one of the maSMP schemas
        if "maSMP" in schema_key:
            jsonld_document["@context"].append({"maSMP": "https://discovery.biothings.io/ns/maSMPProfiles/"})

        # Extract the relevant properties for the given schema
        schema_properties = schema_map[schema_key]["properties"].copy()  # Use a copy to avoid mutating the original

        # Map provided data to the schema properties
        for key, value in data.items():
            if key in schema_properties:
                # Add to the JSON-LD document only if the key exists in the schema properties
                jsonld_document[key] = value

        # # Add non-null properties from schema defaults (i.e., defaults that were not provided in data)
        # jsonld_document.update({key: value for key, value in schema_properties.items() if key not in data and value is not None})

        # Add non-null properties from schema defaults, skipping properties in 'to_be_removed'
        jsonld_document.update({
            key: value
            for key, value in schema_properties.items()
            if key not in data and value is not None and key not in to_be_removed
        })

        return jsonld_document  # Return the dictionary, not a JSON string

    if schema == "maSMP":
        # Generate JSON-LD for both maSMP:SoftwareSourceCode and maSMP:SoftwareApplication
        return {
            "maSMP:SoftwareSourceCode": create_jsonld("maSMP:SoftwareSourceCode"),
            "maSMP:SoftwareApplication": create_jsonld("maSMP:SoftwareApplication")
        }
    else:
        # For other schemas (like CODEMETA), generate the JSON-LD for a single schema
        return create_jsonld(schema)