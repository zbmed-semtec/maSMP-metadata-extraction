import copy
import json
from src.GitHubRepoExtractor import GitHubRepoExtractor
from src.RepoFilesParser import RepoFilesParser
from src.ExternalDataFetcher import ExternalDataFetcher
from src.Utilities import construct_json
from src.constants import CombinedProperties

def process_repository(repo_url, All_properties, schema, access_token=None):
    """
    Processes a GitHub repository to extract metadata and generate a JSON-LD document.
    
    Args:
        repo_url (str): The URL of the GitHub repository.
        All_properties (dict): A dictionary containing extracted metadata properties.
        schema (str): The schema to be used for JSON-LD document generation.
        access_token (str, optional): GitHub access token for authentication.
    
    Returns:
        dict: The constructed JSON-LD document.
    """
    GitExtractor = GitHubRepoExtractor(repo_url, All_properties, access_token)
    All_properties, hasRelease = GitExtractor.process_repo()

    FileParser = RepoFilesParser(repo_url, All_properties, access_token)
    All_properties, DOI, reference_extracted = FileParser.parse_files()

    DataFetcher = ExternalDataFetcher(repo_url, All_properties, DOI, access_token, reference_extracted)
    All_properties = DataFetcher.extract()

    jsonld_document = construct_json(All_properties, schema, hasRelease)
    return jsonld_document

if __name__ == "__main__":
    """
    Main execution block to process a GitHub repository and save the resulting JSON-LD document.
    """
    repo_url = "https://github.com/KnowledgeCaptureAndDiscovery/somef"
    schema = "maSMP"
    access_token = None

    # Reset All_properties to None before each call
    All_properties = copy.deepcopy(CombinedProperties)
    
    # Call the process_repository function
    result = process_repository(repo_url, All_properties, schema, access_token)
    
    # Write the result to a JSON file
    output_file = "output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"Generated JSON-LD Document has been saved to {output_file}")
