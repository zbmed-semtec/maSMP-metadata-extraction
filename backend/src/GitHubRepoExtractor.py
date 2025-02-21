import requests
import time
from src.logger_config import logger
from src import Utilities

class GitHubRepoExtractor:
    """
    A class to extract metadata and properties from a GitHub repository using GitHub's REST API.
    """
    def __init__(self, repo_url, all_properties, access_token=None):
        """
        Initializes the GitHubRepoExtractor instance.
        
        Args:
            repo_url (str): URL of the GitHub repository.
            all_properties (dict): Dictionary to store extracted properties.
            access_token (str, optional): GitHub access token for authentication.
        """
        self.repo_url = repo_url
        self.owner, self.repo = Utilities.extract_repo_info(self.repo_url)
        self.access_token = access_token
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        if access_token:
            self.headers['Authorization'] = f'token {access_token}'
        self.all_properties = all_properties

    def process_repo(self):
        """
        Determines if the repository is hosted on GitHub and extracts its properties.
        
        Returns:
            dict: Updated all_properties dictionary.
        """
        if 'github.com' in self.repo_url:
            self.extract_github_properties()
        else:
            raise ValueError("Unsupported git hosting service.")
        return self.all_properties

    def rate_limit_get(self, url, backoff_rate=2, initial_backoff=1):
        """
        Performs a rate-limited GET request with an exponential backoff strategy.
        
        Args:
            url (str): API URL to send the GET request to.
            backoff_rate (int, optional): Factor by which to increase backoff time. Defaults to 2.
            initial_backoff (int, optional): Initial backoff time in seconds. Defaults to 1.
        
        Returns:
            dict: JSON response from the API.
        """
        while True:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            
            if response.status_code == 403:
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    sleep_time = int(retry_after)
                elif 'X-RateLimit-Remaining' in response.headers and int(response.headers['X-RateLimit-Remaining']) == 0:
                    reset_time = int(response.headers['X-RateLimit-Reset'])
                    sleep_time = max(reset_time - time.time(), 0) + 1
                else:
                    sleep_time = initial_backoff
                    initial_backoff *= backoff_rate
                
                logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                time.sleep(sleep_time)
                continue

            response.raise_for_status()

    def extract_github_properties(self):
        """
        Extracts metadata from the GitHub repository and populates all_properties dictionary.
        """
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo}'
        repo_data = self.rate_limit_get(api_url)

        self.all_properties.update({
            "name": repo_data.get('name'),
            "description": repo_data.get('description'),
            "url": repo_data.get('html_url'),
            "codeRepository": f"{repo_data.get('html_url')}.git",
            "dateCreated": repo_data.get('created_at', '')[:10],
            "dateModified": repo_data.get('updated_at', '')[:10],
            "datePublished": repo_data.get('pushed_at', '')[:10],
            "codemeta:issueTracker": f"{repo_data.get('html_url')}/issues",
            "conditionsOfAccess": "Private" if repo_data.get('private', False) else "Public",
            "isAccessibleForFree": str(not repo_data.get('private', False)),
            "downloadUrl": repo_data.get('archive_url', '').replace('{archive_format}{/ref}', 'zipball/master'),
            "discussionUrl": f"{repo_data.get('html_url')}/discussions" if repo_data.get('has_discussions') else None,
            "hasSourceCode": f"{repo_data.get('html_url')}#id",
            "keywords": repo_data.get('topics') or None,
            "maSMP:versionControlSystem": {"@type": "SoftwareApplication", "@id":"https://www.wikidata.org/wiki/Q186055", "url": "https://git-scm.com/", "name": "Git"},
        })

        # Extract programming languages and contributors
        for endpoint, key in [("/languages", "programmingLanguage"), ("/contributors", "contributor")]:
            try:
                data = self.rate_limit_get(api_url + endpoint)
                self.all_properties[key] = list(data.keys()) if key == "programmingLanguage" else [{"@type": "Person", "url": c['html_url']} for c in data]
            except requests.exceptions.RequestException:
                logger.warning(f"Could not fetch {key} for this repository.")

        # Extract README and CHANGELOG files
        for branch in ['master', 'main']:
            for file, key in [("README.md", "codemeta:readme"), ("CHANGELOG.md", "maSMP:changelog")]:
                url = f"https://github.com/{self.owner}/{self.repo}/blob/{branch}/{file}"
                if Utilities.is_valid_and_reachable(url, self.access_token):
                    self.all_properties[key] = url
                    break

        # Extract license information
        try:
            license_data = self.rate_limit_get(api_url + "/license")
            self.all_properties["license"] = {"name": license_data.get("license", {}).get("name"), "url": license_data.get("license", {}).get("url")}
        except requests.exceptions.RequestException:
            logger.warning("No license found for this repository.")

        # Extract latest release information
        try:
            release_data = self.rate_limit_get(api_url + "/releases/latest")
            self.all_properties.update({"version": release_data.get('tag_name'), "softwareVersion": release_data.get('tag_name')})
        except requests.exceptions.RequestException:
            logger.warning("No releases found for this repository.")
