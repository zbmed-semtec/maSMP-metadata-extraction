from .git_metadata_extractor import process_git_repo
from .parse_files import parse_citation_cff
from .construct_json import construct_json
from .constants import All_properties

def process_repository(repo_url, All_properties, schema, access_token=None):
    process_git_repo(repo_url, All_properties, access_token)
    parse_citation_cff(repo_url, All_properties, access_token)
    jsonld_document = construct_json(All_properties, schema)
    return jsonld_document

if __name__ == "__main__":

    repo_url = "https://github.com/KnowledgeCaptureAndDiscovery/somef"
    schema = "maSMP"
    access_token = None
    
    # Call the process_repository function
    result = process_repository(repo_url, All_properties, schema, access_token)
    
    # Output the result
    print("Generated JSON-LD Document:")
    print(result)