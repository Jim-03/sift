import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EmploymentType(str, enum.Enum):
    """Type of employment"""

    FULL_TIME = "FULL-TIME"
    INTERNSHIP = "INTERNSHIP"
    CONTRACT = "CONTRACT"


class ExperienceLevel(str, enum.Enum):
    """Experience level required  for a job"""

    SENIOR = "SENIOR"
    JUNIOR = "JUNIOR/ENTRY-LEVEL"
    INTERN = "INTERNSHIP"
    MID = "MID-LEVEL"


class LLMJobDto(BaseModel):
    company: str = Field(description="The name of the company advertising the job")
    url: str = Field(
        description="The source link.",
    )
    title: str = Field(
        description="The name of the role being offered. Should NOT include the company name or the experience level.",
    )
    experience_level: ExperienceLevel | None = Field(
        description="The stated experience level (e.g., 'SENIOR', 'JUNIOR/ENTRY-LEVEL', 'MID-LEVEL'). Output null if none is mentioned. Map entry-level to JUNIOR.",
        default=None,
    )
    employment_type: EmploymentType | None = Field(
        description="The stated type of the employment e.g. CONTRACT, FULL-TIME. Output null if it isn't provided"
    )
    description: str | None = Field(
        description="A short summary of the job description. About 50 words in total"
    )
    responsibilities: list[str] = Field(
        description="The tasks the employee will do.",
    )
    requirements: list[str] = Field(
        description="The qualifications required.",
    )
    benefits: list[str] = Field(
        description="Additional perks excluding salary.",
    )
    salary: str | None = Field(
        description="The expected salary. Structure: {currency} {lower} - {higher}. Output null if not provided.",
        default=None,
    )
    deadline: str | None = Field(
        description="The last date to apply in DD-MM-YYYY format. Output null if not mentioned.",
        default=None,
    )


class JobDataDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    url: str
    company: str
    experience_level: ExperienceLevel
    employment_type: EmploymentType
    description: str
    responsibilities: list[str]
    requirements: list[str]
    benefits: list[str]
    salary: str
    applied: bool
    read: bool
    deadline: str | None
    created_at: datetime | None


class StatisticsDto(BaseModel):
    total_jobs: int = Field(description="Number of jobs in the database")
    total_matches: int = Field(
        description="Number of jobs the user profile strongly matches"
    )
    applied: int = Field(description="Number of jobs the user has applied")
    best_match_jobs: list[JobDataDto] = Field(
        description="A list of 5 recent best matching jobs"
    )
    recent_jobs: list[JobDataDto] = Field(description="A list of 5 recent job's found")


class Verdict(str, enum.Enum):
    """Enum to gauge how well the profile matches the job"""

    STRONG = "strong"
    GOOD = "good"
    PARTIAL = "partial"
    WEAK = "weak"
    NONE = "none"


class JobReview(BaseModel):
    reasoning: str = Field(description="Overall reasoning applied by the LLM")
    matches: list[str] = Field(
        description="A list of job requirements met by the user's profile"
    )
    partial: list[str] = Field(description="A list of transferable skills")
    gaps: list[str] = Field(description="Missing gaps that may disqualify the profile")
    verdict: Verdict = Field(
        description="A gauge to determine how well the profile matches the job"
    )


class FullJobDto(JobDataDto):
    job_metadata: JobReview | None = Field(description="LLM-based review")
