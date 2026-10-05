import json
import os

class MetadataManager:
    def __init__(self, metadata_dir: str = None):
        if metadata_dir is None:
            # Default to backend/app/ai/metadata/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.metadata_dir = os.path.join(current_dir, "..", "metadata")
        else:
            self.metadata_dir = metadata_dir

        self.tools = []
        self.glossary = {}

        self.load()

    def _load_json(self, filename: str):
        filepath = os.path.join(self.metadata_dir, filename)
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    def load(self):
        tools_data = self._load_json("tools.json")
        if tools_data:
            self.tools = tools_data

        glossary_data = self._load_json("glossary.json")
        if glossary_data:
            self.glossary = glossary_data

    def get_tools(self):
        return self.tools

    def get_tool_names(self):
        return [tool["name"] for tool in self.tools]

    def get_glossary(self):
        return self.glossary

    def search_glossary(self, query: str) -> dict:
        """Finds any glossary terms that exist in the user's query."""
        query_lower = query.lower()
        results = {}
        for term, meaning in self.glossary.items():
            if term.lower() in query_lower:
                results[term] = meaning
        return results
