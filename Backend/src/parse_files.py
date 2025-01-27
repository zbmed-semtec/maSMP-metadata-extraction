import yaml
import requests
from urllib.parse import urlparse
import logging
import base64
from .utils import find_property

def parse_citation_cff(repo_url, All_properties, access_token=None):
    """Parse citation.cff file and extract author information for GitHub and GitLab."""
    headers = {}
    if access_token:
        headers['Authorization'] = f'token {access_token}' if 'github.com' in repo_url else f'Bearer {access_token}'

    # Parse the repository URL
    parsed_url = urlparse(repo_url)
    parts = parsed_url.path.strip('/').split('/')
    owner, repo = parts[-2], parts[-1]

    branches = ['master', 'main']
    citation_filenames = ['CITATION.cff', 'citation.cff']

    cff_content = None

    # Determine the appropriate URL for the citation file based on the repository URL
    if 'github.com' in repo_url:
        base_url = f'https://api.github.com/repos/{owner}/{repo}/contents/'
        
        for filename in citation_filenames:
            cff_url = f'{base_url}{filename}'
            response = requests.get(cff_url, headers=headers)
            if response.status_code == 200:
                content = response.json()
                if 'content' in content:
                    cff_content = base64.b64decode(content['content']).decode('utf-8')
                    break
        else:
            logging.warning("Unable to find CITATION.cff file in the GitHub repository.")
            return

    elif 'gitlab.com' in repo_url:
        base_url = f'https://gitlab.com/api/v4/projects/{owner}%2F{repo}/repository/files/'
        
        for filename in citation_filenames:
            for branch in branches:
                cff_url = f'{base_url}{filename}/raw?ref={branch}'
                response = requests.get(cff_url, headers=headers)
                if response.status_code == 200:
                    cff_content = response.text
                    break
            else:
                continue
            break
        else:
            logging.warning("Unable to find CITATION.cff file in the GitLab repository.")
            return

    else:
        logging.warning("Unsupported git hosting service. Only GitHub and GitLab are supported.")
        return

    if cff_content is None:
        logging.warning("Unable to fetch CITATION.cff file.")
        return

    try:
        cff_data = yaml.safe_load(cff_content)
    except yaml.YAMLError as e:
        logging.warning(f"Unable to parse citation.cff file: {str(e)}")
        return

    authors = []
    if 'authors' in cff_data:
        for author in cff_data['authors']:
            person = {
                "@type": "Person",
                "familyName": author.get('family-names'),
                "givenName": author.get('given-names')
            }
            if 'orcid' in author:
                person["@id"] = author['orcid']
            authors.append(person)

    if authors:
        All_properties["author"] = authors

    # Define the target keys you want to extract
    target_keys = {
        "alternateName": "title",
        "identifier": "doi",
        "keywords": "keywords"
    }

    All_properties["citation"] = []
    # Extract additional metadata if available using find_property function
    for property_name, target_key in target_keys.items():
        # Use find_property to extract values
        values = find_property(cff_data, target_key)

        if values:
            # Assign to All_properties if multiple values are found or use the first one
            if property_name == "identifier":  # Special case for DOI
                All_properties[property_name] = f"https://doi.org/{values[0]}"
                All_properties["citation"].append({"@type":"Article", "@id": f"https://doi.org/{values[0]}"})
            else:
                All_properties[property_name] = values[0]  # Use the first found value

    # Check for 'preferred-citation' field in the CFF content
    if 'preferred-citation' in cff_data:
        preferred_citation = cff_data['preferred-citation']

        reference_publication = {
            "@type": "ScholarlyArticle"
        }

        if 'doi' in preferred_citation:
            reference_publication["@id"] = f"https://doi.org/{preferred_citation['doi']}"
        
        if 'title' in preferred_citation:
            reference_publication['name'] = preferred_citation['title']

        if 'authors' in preferred_citation:
            reference_publication['author'] = []
            for author in preferred_citation['authors']:
                author_entry = {
                    "@type": "Person",
                    "familyName": author.get('family-names'),
                    "givenName": author.get('given-names'),
                }
                if 'orcid' in author:
                    author_entry["@id"] = author['orcid']
                reference_publication["author"].append(author_entry)
            
        All_properties["codemeta:referencePublication"] = reference_publication