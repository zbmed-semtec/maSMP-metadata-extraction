import ollama
from app.layer_3.plugins.shared.git_platform_base_extractor import GitPlatformBaseExtractor
from app.layer_3.plugins.url_pattern_matcher_plugin import URLPatternMatcher
from app.layer_3.plugins.codeberg.utils import match_license_text, dependency_files
from app.layer_3.plugins.shared.wayback_client import WaybackClient
from app.layer_3.plugins.shared.software_heritage_client import SoftwareHeritageClient
from app.layer_3.plugins.shared.open_alex_client import OpenAlexClient

class LlmNameExtractor(GitPlatformBaseExtractor):
    """schema:name"""

    extracts = {'https://schema.org/name'}

    def extract(self, context, state):
        client = self.get_client(context, state)
        all_readme_text = "------\n".join(
            [str(file.get_content()) 
            for file in client.get_readme_candidate_files()])

        messages = [
            {
                'role': 'system',
                'content': 'You are a metadata extraction assistant. Extract only the requested information with no additional commentary.'
            },
            {
                'role': 'user',
                'content': f"""Extract the name of the software project from the following README content. Respond with ONLY the project name.

    README content:
    {all_readme_text}"""
            }
        ]

        response = ollama.chat(
            model='phi4-mini',
            messages=messages,
            options={'temperature': 0.1}
        )

        project_name = response['message']['content'].strip()
        state.metadata_collector.collect("LLM", "https://schema.org/name", project_name, 0.80)
        return state