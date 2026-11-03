"""Module handling job extraction using ollama"""

import os

from dotenv import load_dotenv
from ollama import AsyncClient

from src.dto.job_dto import LLMJobDto
from src.services.ollama_service import JobCompensation, JobContent, JobMetadata

load_dotenv()


class JobExtractor:
    """Service handling job data extraction"""

    def __init__(self):
        self.__model = os.getenv("OLLAMA_EXTRACTION_MODEL", "gemma3")
        self.__client = AsyncClient()

    async def extract(self, listing: str) -> LLMJobDto:
        metadata = await self.extract_metadata(listing)
        description = await self.extract_description(listing)
        content = await self.extract_content(listing)
        compensation = await self.extract_compensation(listing)
        url = await self.extract_url(listing)

        salary = None
        if compensation.salary:
            if compensation.salary.maximum is not None:
                salary = f"{compensation.salary.currency or ''} {compensation.salary.minimum} - {compensation.salary.maximum}"
            else:
                salary = f"{compensation.salary.currency or ''} {compensation.salary.minimum}"

        return LLMJobDto(
            **metadata.model_dump(),
            description=description,
            **content.model_dump(),
            benefits=compensation.benefits,
            url=url,
            salary=salary,
        )

    async def extract_url(self, listing: str) -> str:
        system_prompt = """
        Extract the URL where the job posting is found.
        
        ## Rules:
        - The URL is located at the top of a listing
        - Respond with the URL **ONLY**.
        - **DO NOT** create/generate your own URL
        - If no URL is provided, respond with an empty string
        """

        response = await self.__client.chat(
            model=self.__model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": listing},
            ],
            options={
                "temperature": 0,
                "seed": 42,
                "top_k": 0,
                "top_p": 0.1,
            },
            keep_alive="5m",
        )

        return str(response.message.content)

    async def extract_metadata(self, listing: str) -> JobMetadata:
        """Extract extra details about a job

        Args:
            listing: Scraped job listing

        Returns:
            (JobMetadata): Extra details about a job

        """
        system_prompt = """
        You are a helpful assistant tasked to extract a structured metadata JSON object
         from text scraped from a job board.
        
        ## Rules:
        - Extract **ONLY** what's provided.
        - Do not generate content that isn't showed in the text.
        - Use the instructions & examples from the object structure on how to generate the metadata
        """

        response = await self.__client.chat(
            model=self.__model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": listing},
            ],
            options={
                "temperature": 0,
                "seed": 42,
                "top_k": 10,
                "top_p": 0.3,
            },
            format=JobMetadata.model_json_schema(),
            keep_alive="5m",
        )

        return JobMetadata.model_validate_json(str(response.message.content))

    async def extract_description(self, listing: str) -> str:
        """Generate a short summary of the job's description

        Args:
            listing: Scraped job listing

        Returns:
            (str): Short summary of the job's description

        """
        system_prompt = """
        You have been tasked to summarize and provide a description from a text
        scraped from a job board.
        
        ## Rules:
        - Use the provided text **ONLY**. Do not generate text outside the provided text.
        - Keep the description short maxing at 100 words.
        - The description should be in third person addressing an applicant
        
        ## Examples:
        - Company ABC is looking for an accountant to manage their day-to-day finances.
        - Engineer required in airline X to model an airplane
        """
        response = await self.__client.chat(
            model=self.__model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": listing},
            ],
            options={
                "temperature": 1,
                "top_k": 5,
                "top_p": 0.3,
                "num_ctx": 4096,
                "num_predict": 32,
            },
            keep_alive="5m",
        )

        return str(response.message.content)

    async def extract_content(self, listing: str) -> JobContent:
        """Extract a job's main part of a job description

        Args:
            listing: Scraped job listing

        Returns:
            (JobContent): Main part of a job description

        """
        system_prompt = """
        You are tasked to extract the main part of a job description from text
        scraped from a job board.
        
        ## Rules:
        - Use **ONLY** the provided text.
        - Do not generate text outside what's provided.
        - Use description and examples from the JSON structure
        """

        response = await self.__client.chat(
            model=self.__model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": listing},
            ],
            options={
                "temperature": 0,
                "seed": 42,
                "top_k": 5,
                "top_p": 0.3,
            },
            format=JobContent.model_json_schema(),
            keep_alive="5m",
        )

        return JobContent.model_validate_json(str(response.message.content))

    async def extract_compensation(self, listing: str) -> JobCompensation:
        """Extract salary and benefits of a job

        Args:
            listing: Scraped job listing

        Returns:
            (JobCompensation): Salary and benefits of a job

        """
        system_prompt = """
        You are a helpful extraction assistant. Your task is to extract compensation from
        scraped text scraped from a job board.
        
        ## Rules:
        - Use the provided text **ONLY**. Do not generate text outside the provided text.
        """

        response = await self.__client.chat(
            model=self.__model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": listing},
            ],
            options={
                "temperature": 0,
                "seed": 42,
                "top_k": 5,
                "top_p": 0.3,
            },
            keep_alive="5m",
            format=JobCompensation.model_json_schema(),
        )

        return JobCompensation.model_validate_json(str(response.message.content))
