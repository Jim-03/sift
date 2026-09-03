import os
from datetime import datetime

from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import ContentEmbedding

from dto import JobListings

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

    def extract(self, jobs: list[str]) -> JobListings:
        """Retrieve a list of jobs from scraped content

        Args:
            jobs (list[str]): A list of scrape content

        Returns:
            (JobListings): An object containing a list of job objects
        """
        if not jobs:
            raise Exception("No jobs content provided!")

        SYSTEM_PROMPT = f"""
        You are a helpful extraction assistant. You have been provided a list of
        scraped HTML content containing a job description. Your task is to extract
        the job description from the content following the strict rules at 
        </importantInstructions>
        
        <importantInstructions>
        1. Extract only the provided job details from the scraped data.
        2. For any content that doesn't contain a job description, set the 
           'is_valid_job' property to false.
        3. **DO NOT** generate any content that isn't provided in the description.
        4. Dates may always be mixed up between month and  day, check the date at
           </date> to determine the difference.
        5. All date formats should be in dd-mm-YYYY format  
        </importantInstructions>
        
        <date>
        The current date in dd-mm-YYYY format is {datetime.now().today().strftime("%d-%m-%Y")}
        </date>
        """

        interactions = self.__client.interactions.create(
            model="gemini-3.1-flash-lite",
            system_instruction=SYSTEM_PROMPT,
            input=", ".join(jobs),
            store=False,
            generation_config={"temperature": 0.1},
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": JobListings.model_json_schema(),
            },
        )

        results = interactions.output_text

        if not results:
            raise Exception("Gemini failed to generate response")

        return JobListings.model_validate_json(results)
