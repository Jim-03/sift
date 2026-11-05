"""Module handling Gemini calls"""

from dotenv import load_dotenv
from google.genai import Client, types

from src.dto.job_dto import LLMJobDto
from src.services.ollama_service import JobMatchResult

load_dotenv()

retry_config = types.HttpRetryOptions(
    initial_delay=5,
    attempts=3,
    max_delay=60,
    exp_base=10,
    jitter=3,
    http_status_codes=[503],
)
http_options = types.HttpOptions(retry_options=retry_config, timeout=120 * 1000)
with open("user.md", "r") as f:
    profile = f.read()


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

    async def evaluate(
        self, id: str, requirements: list[str]
    ) -> tuple[JobMatchResult, str]:
        """Assess fitness against profile

        Args:
            requirements: A list of job requirements

        Returns:
            (JobMatchResult): Job fit assessment

        """
        system_prompt = f"""
        You are a senior recruitment manager and assessor in charge of reviewing an applicants profile against a job's requirements.

        ## JOB REQUIREMENTS:
        {requirements}

        ## Rules:
        - Study the entire profile first before making a judgment call.
        - You MUST review each requirement against the applicant's profile.
        - For each requirement, justify whether the profile meets the requirement or not.
        - Allow transferable skills and elaborate what's missing.
        - Do not use personal pronouns in your response.
        - A requirement should only appear once and not in multiple fields i.e. If the finding is a 'partial', it should remain in partial ALONE and not a 'gap' too!

        ## Example output:
        - Minimum education level attained.
        - No proven professional experience.
        - Proven experience in XYZ but no extensive usage of XYZ in field 123
        """

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=JobMatchResult,
            store=False,
            http_options=http_options,
        )

        chat = self.__client.aio.chats.create(
            model="gemini-3.5-flash-lite", config=config
        )

        result = await chat.send_message(
            "\n-".join(f"""
        ## APPLICANT PROFILE
        {profile}
        """)
        )

        return JobMatchResult.model_validate_json(str(result.text)), id
