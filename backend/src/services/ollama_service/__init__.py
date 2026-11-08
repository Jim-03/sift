from enum import Enum

from pydantic import BaseModel, Field

from src.dto.job_dto import EmploymentType, ExperienceLevel, Verdict


class JobMetadata(BaseModel):
    company: str = Field(description="The name of the company offering the job")
    title: str = Field(
        description="""
    The name of the position being offered.
    Shouldn't contain the name of the company.
    Shouldn't contain the experience level e.g. SENIOR, JUNIOR e.t.c.
    """
    )
    experience_level: ExperienceLevel | None = Field(
        default=None,
        description="""
            The experience level required to apply for the job.
            If the level isn't provided, you **MUST** output null.
            JUNIOR and ENTRY_LEVEL are one and the same level.
            DO not infer from anywhere else in the text. Use **ONLY** what's mentioned. 
            """,
    )
    employment_type: EmploymentType | None = Field(
        default=None,
        description="""
        The stated duration of employment. Use **ONLY** what's stated. If it isn't mentioned, output null
        """,
    )
    deadline: str | None = Field(
        default=None,
        description="""
            The stated last date of application.
            Use the format → dd-mm-yyyy.
            """,
        examples=["11-11-2026", "30-10-2023"],
    )


class JobContent(BaseModel):
    responsibilities: list[str] = Field(
        description="A list of tasks the employee will do on their job",
        examples=[
            ["manage staff", "attend meetings"],
            ["Develop software", "Debug errors"],
        ],
    )
    requirements: list[str] = Field(
        description="""
        A list of requirements an applicant should have in order to apply for the job.
        Do not infer from what's listed
        """
    )


class Salary(BaseModel):
    minimum: float | None = Field(
        description="The minimum salary offered by the job",
        examples=["30,000", "55,000"],
    )
    maximum: float | None = Field(
        description="The maximum salary offered by the job",
        examples=["90,000", "100,000"],
    )
    currency: str | None = Field(
        description="The currency of the salary",
        examples=["USD", "KES", "AUD"],
    )


class JobCompensation(BaseModel):
    salary: Salary | None = Field(
        description="""
            The salary offered by the job.
            If it isn't provided, you **MUST** output null.
            If it's a single value, output it in the minimum value **ONLY**.
            """
    )
    benefits: list[str] = Field(
        description="A list of benefits the employee will receive on their job",
    )



class JobMatchResult(BaseModel):
    reasoning: str = Field(
        description="Step-by-step reasoning evaluating the applicant's profile against each job requirement before categorizing findings. This ensures logical alignment."
    )
    matches: list[str] = Field(
        description="A list of findings that suggest the applicant meets the job requirements. Keep each finding at one sentence max, using objective third-person tense."
    )
    partial: list[str] = Field(
        description="A list of transferable skills that describes how the profile is nearly reaching the requirements. Keep each finding at one sentence max, using objective third-person tense."
    )
    gaps: list[str] = Field(
        description="A list of missing justifications detailing where the applicant falls short. Keep each finding at one sentence max, using objective third-person tense."
    )
    verdict: Verdict = Field(
        description="""
        Overall review describing if the applicant is fit for the role.
         **strong:** Highly suited for the job
         **good:** Can proceed but with light checks
         **partial:** Can proceed but with heavy checks
         **weak:** Highly unlikely to get to the final stage
         **none:** Shouldn't be considered at all 
        """
    )
