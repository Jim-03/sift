import enum

from pydantic import BaseModel, Field


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
