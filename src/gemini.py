import os

from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import ContentEmbedding

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")


class Gemini:
    def __init__(self):
        self.__client: Client = Client(api_key=API_KEY)

    def embed(self, listings: list[str] | str) -> list[ContentEmbedding]:
        """Convert texts to vectors

        Args:
            listings (list[str] | str): List of texts or a text to be embedded

        Returns:
            list[ContentEmbedding]: A dense vector representation of the input data
        """

        if not listings:
            raise Exception("Provide data to be embedded!")

        result = self.__client.models.embed_content(
            model="gemini-embedding-2", contents=listings
        )

        embeddings = result.embeddings

        if not embeddings:
            raise Exception("Embedding failed!")

        return embeddings
