import re
import requests
import logging
from urllib.parse import urlparse
from src.constants import CODEMETA, maSMP_SoftwareSourceCode, maSMP_SoftwareApplication, to_be_removed

def is_valid_and_reachable(url, access_token=None):
    """
    Checks if a given URL is valid and reachable.
    
    Args:
        url (str): The URL to validate and check reachability.
        access_token (str, optional): Authentication token for private repositories.
    
    Returns:
        bool: True if the URL is valid and reachable, False otherwise.
    """
    parsed_url = urlparse(url)
    
    if not all([parsed_url.scheme, parsed_url.netloc]):
        return False

    headers = {}
    if access_token:
        if 'github.com' in parsed_url.netloc:
            headers['Authorization'] = f'token {access_token}'
        elif 'gitlab.com' in parsed_url.netloc:
            headers['Authorization'] = f'Bearer {access_token}'

    if 'github.com' in parsed_url.netloc and '/blob/' in url:
        parts = parsed_url.path.split('/')
        url = f"https://raw.githubusercontent.com/{parts[1]}/{parts[2]}/{'/'.join(parts[4:])}"

    try:
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
    
def extract_repo_info(repo_url):
    """
    Extracts the owner and repository name from a repository URL.
    
    Args:
        repo_url (str): The repository URL.
    
    Returns:
        tuple: (owner, repository name) or (None, None) if extraction fails.
    """
    parsed_url = urlparse(repo_url)
    parts = parsed_url.path.strip('/').split('/')
    if len(parts) < 2: 
        return None, None
    return parts[-2], parts[-1]

def find_property(data, target_key):
    """
    Recursively searches for a specific key in a nested dictionary or list.
    
    Args:
        data (dict or list): The dataset to search within.
        target_key (str): The key to find.
    
    Returns:
        list: A list of found values associated with the target key.
    """
    found_values = []

    if isinstance(data, dict):
        if target_key in data:
            found_values.append(data[target_key])
        for value in data.values():
            found_values.extend(find_property(value, target_key))

    elif isinstance(data, list):
        for item in data:
            found_values.extend(find_property(item, target_key))

    elif isinstance(data, str):
        if re.search(rf'\b{target_key}\s*:\s*(.*)', data, re.IGNORECASE):
            match = re.search(rf'\b{target_key}\s*:\s*(.*)', data, re.IGNORECASE)
            if match:
                found_values.append(match.group(1).strip())

    return found_values  

def check_zenodo_badge(readme_url):
    """
    Fetches the README file from the given URL and checks for Zenodo badge links.
    
    Args:
        readme_url (str): The URL of the README file.
    
    Returns:
        list: A list of valid Zenodo DOI URLs found in the README.
    """
    try:
        response = requests.get(readme_url)
        if response.status_code == 200:
            readme_content = response.text
            zenodo_pattern = r'https://(?:doi\.org/(\d+\.\d+/zenodo\.\d+)|zenodo\.org/records/(\d+))'
            matches = re.findall(zenodo_pattern, readme_content)
            extracted_ids = {doi if doi else f'10.5281/zenodo.{record_id}' for doi, record_id in matches}
            extracted_urls = {f"https://doi.org/{doi}" for doi in extracted_ids}
            return [url for url in extracted_urls if is_valid_and_reachable(url)]
    except Exception as e:
        logging.error(f"Error checking Zenodo badge: {e}")
    return []

def fetch_github_file(url, access_token=None):
    """
    Fetches a file from a GitHub repository.
    
    Args:
        url (str): The file URL.
        access_token (str, optional): Authentication token for private repositories.
    
    Returns:
        requests.Response: The response object containing the file content.
    """
    headers = {}
    if access_token:
        headers['Authorization'] = f'token {access_token}'
    response = requests.get(url, headers=headers)
    return response

def construct_json(data, schema):
    """
    Constructs a JSON-LD document from extracted data and a schema.
    
    Args:
        data (dict): Extracted metadata properties.
        schema (str): The schema type (e.g., 'CODEMETA', 'maSMP').
    
    Returns:
        dict: A JSON-LD document.
    """

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

        jsonld_document = {
            "@context": [
                "http://schema.org/",
                {"codemeta": "https://w3id.org/codemeta/3.0"}
            ],
            "@type": schema_map[schema_key]["type"]
        }

        if "maSMP" in schema_key:
            jsonld_document["@context"].append({"maSMP": "https://discovery.biothings.io/ns/maSMPProfiles/"})

        schema_properties = schema_map[schema_key]["properties"].copy()  

        for key, value in data.items():
            if key in schema_properties:
                jsonld_document[key] = None if isinstance(value, list) and not value else value

        jsonld_document.update({
            key: value
            for key, value in schema_properties.items()
            if key not in data and value is not None and key not in to_be_removed
        })

        return jsonld_document  

    if schema == "maSMP":
        return {
            "maSMP:SoftwareSourceCode": create_jsonld("maSMP:SoftwareSourceCode"),
            "maSMP:SoftwareApplication": create_jsonld("maSMP:SoftwareApplication")
        }
    else:
        return create_jsonld(schema)