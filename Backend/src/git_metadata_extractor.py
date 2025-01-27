import requests
import time
import logging
from urllib.parse import urlparse
import base64
from .utils import is_valid_and_reachable

def rate_limit_get(url, headers=None, backoff_rate=2, initial_backoff=1):
    """Perform a rate-limited GET request."""
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
            if int(response.headers['X-RateLimit-Remaining']) == 0:
                reset_time = int(response.headers['X-RateLimit-Reset'])
                sleep_time = max(reset_time - time.time(), 0) + 1
                logging.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                time.sleep(sleep_time)
            else:
                logging.warning(f"Rate limit error. Backing off for {initial_backoff} seconds.")
                time.sleep(initial_backoff)
                initial_backoff *= backoff_rate
        else:
            response.raise_for_status()

def extract_github_properties(repo_url, All_properties, access_token=None):
    """Extract properties from a GitHub repository."""
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if access_token:
        headers['Authorization'] = f'token {access_token}'

    # Parse the GitHub URL
    parsed_url = urlparse(repo_url)
    print(parsed_url)
    _, owner, repo = parsed_url.path.split('/')

    # Get repository information (includes most of the data we need)
    api_url = f'https://api.github.com/repos/{owner}/{repo}'
    repo_data = rate_limit_get(api_url, headers)

    # Update All_properties with data from the main API call
    All_properties.update({
        "name": repo_data.get('name'),
        "description": repo_data.get('description'),
        "url": repo_data.get('html_url'),
        "codeRepository": repo_data.get('html_url'),
        "dateCreated": repo_data.get('created_at')[0:10],
        "dateModified": repo_data.get('updated_at')[0:10],
        "datePublished": repo_data.get('pushed_at')[0:10],
        "codemeta:issueTracker": repo_data.get('issues_url').replace('{/number}', ''),
        "maSMP:versionControlSystem": {"@type": "SoftwareApplication", "@id":"https://www.wikidata.org/wiki/Q186055", "url": "https://git-scm.com/", "name": "Git"},
        "conditionsOfAccess": "Private" if repo_data.get('private', False) else "Public",
        "keywords": repo_data.get('topics', []),
        "archivedAt": repo_data.get('archive_url').replace('{archive_format}{/ref}', 'zipball/master'),
        "downloadUrl": repo_data.get('archive_url').replace('{archive_format}{/ref}', 'zipball/master'),
        "discussionUrl": f"{repo_data.get('html_url')}/discussions" if repo_data.get('has_discussions') else None,
    })

    # Get Programming Languages (if available)
    languages_url = f'{api_url}/languages'
    try:
        languages_data = rate_limit_get(languages_url, headers)
        All_properties["programmingLanguage"] = list(languages_data.keys())
    except requests.exceptions.HTTPError:
        logging.warning("Unable to fetch programming languages for this repository.")

    # Get link to latest release for the target product
    targetProduct_url = f'{api_url}/releases'
    try:
        targetProduct_data = rate_limit_get(targetProduct_url, headers)
        All_properties["targetProduct"] = targetProduct_data[0].get('html_url')
    except requests.exceptions.HTTPError:
        logging.warning("Unable to fetch target product for this repository.")

    # Get README URL from both 'master' and 'main' branches
    for branch in ['master', 'main']:
        readme_url = f'https://github.com/{owner}/{repo}/blob/{branch}/README.md'
        if is_valid_and_reachable(readme_url, access_token):
            All_properties["codemeta:readme"] = readme_url
            break  # Exit the loop if a valid README URL is found

    # Get License information (if available)
    license_url = f'{api_url}/license'
    try:
        license_data = rate_limit_get(license_url, headers)
        data = license_data.get('license')
        license_dict = {"name": data.get('name'), "url": data.get('url')}
        All_properties["license"] = license_dict
    except requests.exceptions.HTTPError:
        logging.warning("No license found for this repository.")

    # Get contributors (if available)
    contributors_url = f'{api_url}/contributors'
    try:
        contributors_data = rate_limit_get(contributors_url, headers)
        contributors_list = []
        for contributor in contributors_data:
            contributors_list.append({"@type": "Person", "url": contributor['html_url']})
        All_properties["contributor"] = contributors_list
    except requests.exceptions.HTTPError:
        logging.warning("Unable to fetch contributors for this repository.")
            

    # Get release information (if available)
    releases_url = f'{api_url}/releases/latest'
    try:
        release_data = rate_limit_get(releases_url, headers)
        All_properties.update({
            "version": release_data.get('tag_name'),
            "softwareVersion": release_data.get('tag_name'),
            "releaseNotes": releases_url,
        })
    except requests.exceptions.HTTPError:
        logging.warning("No releases found for this repository.")

    # Check for changelog
    changelog_url = f'{api_url}/commits'
    if is_valid_and_reachable(changelog_url, access_token):
        All_properties["maSMP:changelog"] = changelog_url
    

def extract_gitlab_properties(repo_url, All_properties, access_token=None):
    """Extract properties from a GitLab repository."""
    headers = {}
    if access_token:
        headers['PRIVATE-TOKEN'] = access_token

    # Parse the GitLab URL
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip('/').split('/')
    project_path = '/'.join(path_parts)

    # Get repository information (includes most of the data we need)
    api_url = f'https://gitlab.com/api/v4/projects/{project_path}'
    repo_data = requests.get(api_url, headers=headers).json()

    # Update All_properties with data from the main API call
    All_properties.update({
        "name": repo_data.get('name'),
        "description": repo_data.get('description'),
        "url": repo_data.get('web_url'),
        "codeRepository": repo_data.get('web_url'),
        "dateCreated": repo_data.get('created_at')[0:10],
        "dateModified": repo_data.get('last_activity_at')[0:10],
        "license": repo_data.get('license', {}).get('name'),
        "codemeta:issueTracker": f"{repo_data.get('web_url')}/-/issues",
        "maSMP:versionControlSystem": {"@type": "SoftwareApplication", "@id":"https://www.wikidata.org/wiki/Q186055", "url": "https://git-scm.com/", "name": "Git"},
        "conditionsOfAccess": "Private" if repo_data.get('private', False) else "Public",
        "programmingLanguage": list(repo_data.get('languages', {}).keys()),
        "keywords": repo_data.get('topics', []),
        "archivedAt": repo_data.get('archive_url').replace('{archive_format}{/ref}', 'zipball/master'),
        "discussionUrl": f"{repo_data.get('html_url')}/discussions" if repo_data.get('has_discussions') else None,
    })

    # Get Programming Languages (if available)
    languages_url = f'{api_url}/languages'
    try:
        languages_data = rate_limit_get(languages_url, headers)
        All_properties["programmingLanguage"] = list(languages_data.keys())
    except requests.exceptions.HTTPError:
        logging.warning("Unable to fetch programming languages for this repository.")

    # Get link to latest release for the target product
    targetProduct_url = f'{api_url}/releases'
    try:
        targetProduct_data = rate_limit_get(targetProduct_url, headers)
        All_properties["targetProduct"] = targetProduct_data[0].get('html_url')
        # NOTE: It can also be : 1) zipball_url 2) tarball_url
    except requests.exceptions.HTTPError:
        logging.warning("Unable to fetch target product for this repository.")

    # Get README url (if available)
    readme_url = f'{api_url}/blob/master/README.md'
    if is_valid_and_reachable(readme_url, access_token):
        All_properties["codemeta:readme"] = readme_url

    # Get release information (if available)
    releases_url = f'{api_url}/releases'
    try:
        releases_data = requests.get(releases_url, headers=headers).json()
        if releases_data:
            latest_release = releases_data[0]
            All_properties.update({
                "version": latest_release.get('tag_name'),
                "softwareVersion": latest_release.get('tag_name'),
                "releaseNotes": releases_url,
            })
    except requests.exceptions.HTTPError:
        logging.warning("No releases found for this repository.")

    # Get contributors (if available)
    contributors_url = f'{api_url}/users'
    try:
        contributors_data = requests.get(contributors_url, headers=headers).json()
        All_properties["contributor"] = [contributor['username'] for contributor in contributors_data]
    except requests.exceptions.HTTPError:
        logging.warning("Unable to fetch contributors for this repository.")

    # Check for changelog
    changelog_url = f'{api_url}/commits'
    if is_valid_and_reachable(changelog_url, access_token):
        All_properties["maSMP:changelog"] = changelog_url

def process_git_repo(repo_url, All_properties, access_token=None):
    """Process a git repository and extract properties."""
    if 'github.com' in repo_url:
        extract_github_properties(repo_url, All_properties, access_token)
    elif 'gitlab.com' in repo_url:
        extract_gitlab_properties(repo_url, All_properties, access_token)
    else:
        raise ValueError("Unsupported git hosting service. Only GitHub and GitLab are supported.")