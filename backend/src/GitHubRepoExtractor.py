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
        self.last_commit_date = None
        self.release_info = {"hasRelease": False, "tag_name": None, "release_date": None}

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
        return self.all_properties, self.release_info["hasRelease"]

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

        # Extract README file
        for branch in ['master', 'main']:
            readme_url = f"https://github.com/{self.owner}/{self.repo}/blob/{branch}/README.md"
            if Utilities.is_valid_and_reachable(readme_url, self.access_token):
                self.all_properties["codemeta:readme"] = readme_url
                break

        # Extract CHANGELOG file
        for branch in ['master', 'main']:
            changelog_url = f"https://github.com/{self.owner}/{self.repo}/blob/{branch}/CHANGELOG.md"
            if Utilities.is_valid_and_reachable(changelog_url, self.access_token):
                self.all_properties["maSMP:changelog"] = changelog_url
                break

        # Extract license information
        try:
            license_data = self.rate_limit_get(api_url + "/license")
            self.all_properties["license"] = {"name": license_data.get("license", {}).get("name"), "url": license_data.get("license", {}).get("url")}
        except requests.exceptions.RequestException:
            logger.warning("No license found for this repository.")

        # Extract last commit info
        try:
            commit_data = self.rate_limit_get(api_url + "/commits")
            commit_date = commit_data[0]["commit"]["committer"]["date"]
            self.last_commit_date  = str(Utilities.format_date(commit_date)[:10])
        except:
            logger.warning("Last commit date cannot be fetched")

        # Extract latest release information
        try:
            release_data = self.rate_limit_get(api_url + "/releases/latest")
            if release_data:
                self.release_info["hasRelease"] = True
                self.release_info["tag"] = release_data.get("tag_name")
                self.release_info["release_date"] = str(Utilities.format_date(release_data.get("published_at"))[:10])
        except requests.exceptions.RequestException:
            logger.warning("No releases found for this repository.")

        lastest_release_flag = Utilities.compare_dates(self.last_commit_date, self.release_info["release_date"])
        if self.release_info["hasRelease"]: # Assign softwareVersion if there is a release associated
            self.all_properties["softwareVersion"] = self.release_info["tag"]
            if lastest_release_flag: # Assign version only if the last commit is behind or same as the latest release date
                self.all_properties["version"]= self.release_info["tag"]
