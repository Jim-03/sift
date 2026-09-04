import os
from datetime import datetime

from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import ContentEmbedding

from src.data import get_data
from src.dto import Job, JobListings, MetadataList

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

  def make_notes(self, jobs: list[Job]):
    """Make Gemini reviewed notes based on user profile and job description

    Args:
        jobs (list[Job]): List of job data

    Returns:
         (MetadataList): List of notes
    """
    if not jobs:
      raise Exception("No jobs for note making!")

    SYSTEM_PROMPT = f"""
        You are a helpful review assistant. You are required to make a brief 
        review of a user's profile against a list of job objects. The details are
        provided in </context>. Follow the instructions at </instructions> on how
        to review.
        
        <context>
        **PROFILE SUMMARY:** {get_data("summary")}
        **SKILLS:** {get_data("skills")}
        </context>
        
        <instructions>
        1. Provide a brief review assessing the user's match against each job.
        2. Keep the review brief. The review can include (not strict) the overall
           review, the fitness score or the skill gap.
        3. Assume the response will be read in an email.
        4. Use the value from the 'id' property to determine which response 
           belongs to which job.
        5. Be brutally honest on everything.
        6. Use a standard format for every review.
        </instructions>
        """

    interaction = self.__client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=", ".join([str(job) for job in jobs]),
        system_instruction=SYSTEM_PROMPT,
        response_format={
          "mime_type": "application/json",
          "type": "text",
          "schema": MetadataList.model_json_schema(),
        },
    )

    result = interaction.output_text

    if not result:
      raise Exception("Failed to review jobs")

    return MetadataList.model_validate_json(result)
