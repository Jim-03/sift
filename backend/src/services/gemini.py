"""Module handling Gemini calls"""

from dotenv import load_dotenv
from google.genai import Client, types

from src.dto.job_dto import LLMJobDto

load_dotenv()


class GeminiService:
    """Service class handling the business logic behind Gemini calls"""

    def __init__(self):
        self.__client = Client()

    async def extract_job(self, scraped_text: str) -> LLMJobDto:
        """Extract structural job details from scraped web text

        Args:
            scraped_text: Text scraped from a website

        Returns:
            (LLMJobDto): Structured job data

        """
        system_prompt = """
        You are a data extraction expert. You've been tasked to extract information from text scraped from a website and
        output in a specified structure.
        
        Use the provided instructions in the JSON object on how to extract the job details.
        Study the examples on how to output the values. 
        """

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0,
            response_schema=LLMJobDto,
            store=False,
        )

        chat = self.__client.aio.chats.create(
            model="gemini-3.1-flash-lite", config=config
        )

        response = await chat.send_message(scraped_text)

        return LLMJobDto.model_validate_json(str(response.text))
