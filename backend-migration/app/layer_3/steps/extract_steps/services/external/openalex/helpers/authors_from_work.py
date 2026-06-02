"""Parse OpenAlex work JSON into author dicts (used by multiple property steps)."""


def authors_from_openalex_work(work_data: dict) -> list[dict]:
    """Normalize authorships from an OpenAlex work payload into Person-shaped dicts."""
    authors: list[dict] = []
    for author_entry in work_data.get("authorships", []) or []:
        author = author_entry.get("author", {}) if isinstance(author_entry, dict) else {}
        display_name = author.get("display_name")
        if not display_name:
            continue
        name_parts = display_name.rsplit(" ", 1)
        if len(name_parts) == 2:
            given_name, family_name = name_parts
        else:
            given_name, family_name = display_name, ""
        person = {"@type": "Person", "familyName": family_name, "givenName": given_name}
        if author.get("orcid"):
            person["@id"] = author["orcid"]
        authors.append(person)
    return authors


__all__ = ["authors_from_openalex_work"]
