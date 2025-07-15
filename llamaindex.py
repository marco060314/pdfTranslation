from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
import os

class TranslationMemoryIndex:
    def __init__(self, txt_file_path, model="gpt-4o", api_key_path="api.txt"):
        with open(api_key_path, "r") as f:
            api_key = f.read().strip()

        self.txt_file_path = txt_file_path
        self.model = model
        Settings.llm = OpenAI(model=model, api_key=api_key)

        # Build index
        documents = SimpleDirectoryReader(input_files=[self.txt_file_path]).load_data()
        self.index = VectorStoreIndex.from_documents(documents)
        self.query_engine = self.index.as_query_engine(similarity_top_k=3)

    def query(self, input_text):
        response = self.query_engine.query(input_text)
        return response.response.strip()
