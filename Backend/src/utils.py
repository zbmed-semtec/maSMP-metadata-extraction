import re
import requests
from urllib.parse import urlparse

def is_valid_and_reachable(url, access_token=None):
    """
    Check if a URL has a valid structure and is reachable.
    
    Args:
    url (str): The URL to check.
    access_token (str, optional): Access token for authenticated requests.
    
    Returns:
    bool: True if the URL is valid and reachable, False otherwise.
    """
    parsed_url = urlparse(url)
    
    # Check if the URL has a valid structure
    if not all([parsed_url.scheme, parsed_url.netloc]):
        return False

    # Prepare headers with access token if provided
    headers = {}
    if access_token:
        if 'github.com' in parsed_url.netloc:
            headers['Authorization'] = f'token {access_token}'
        elif 'gitlab.com' in parsed_url.netloc:
            headers['Authorization'] = f'Bearer {access_token}'

    # For GitHub, convert blob URLs to raw content URLs
    if 'github.com' in parsed_url.netloc and '/blob/' in url:
        parts = parsed_url.path.split('/')
        url = f"https://raw.githubusercontent.com/{parts[1]}/{parts[2]}/{'/'.join(parts[4:])}"

    # Check if the URL is reachable
    try:
        # Use GET instead of HEAD as some servers might not support HEAD requests
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def find_property(data, target_key):
    """
    Recursively search for a specific key in a nested dictionary or list,
    and also search for the target_key as text in any string.

    :param data: The input data (dict, list, or string).
    :param target_key: The key or phrase to search for.
    :return: A list of values associated with the target_key.
    """
    found_values = []

    if isinstance(data, dict):
        # Check if the target key exists in the current dictionary
        if target_key in data:
            found_values.append(data[target_key])
        
        # Recursively search in each value
        for value in data.values():
            found_values.extend(find_property(value, target_key))

    elif isinstance(data, list):
        # If data is a list, search in each item
        for item in data:
            found_values.extend(find_property(item, target_key))

    elif isinstance(data, str):
        # Check if the target_key appears in the string
        if re.search(rf'\b{target_key}\s*:\s*(.*)', data, re.IGNORECASE):
            # Extract value after the key using regex
            match = re.search(rf'\b{target_key}\s*:\s*(.*)', data, re.IGNORECASE)
            if match:
                found_values.append(match.group(1).strip())

    return found_values  # Return the list of found values