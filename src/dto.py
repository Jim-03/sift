import uuid
from datetime import date, timedelta

from pydantic import BaseModel, Field


class Job(BaseModel):
    id: str = Field(
        default_factory=lambda: uuid.uuid4().hex,
        description="A system auto-generated unique identifier",
    )
    is_valid_job: bool = Field(
        description="Property to confirm if the provided data is valid job description"
    )
    company_name: str = Field(
        default="Unknown", description="The name of the company offering the position"
    )
    source_url: str = Field(
        description="The link from which the job posting was extracted"
    )
    location: str = Field(
        default="Unknown",
        description="The location where the posting/company is located",
        examples=["Nairobi, Kenya", "Remote", "Kenya"],
    )
    title: str = Field(
        description="The role name", examples=["Junior Software developer"]
    )
    salary: str = Field(
        default="Unknown",
        description="The salary range in the format (min - max) or the actual salary",
        examples=["44,000 - 55,000", "50,000"],
    )
    currency: str = Field(
        default="Unknown",
        description="The currency of the salary",
        examples=["KES", "USD"],
    )
    description: str = Field(description="The overall job description")
    benefits: list[str] | None = Field(
        default=None, description="A list of benefits of working in that job"
    )
    requirements: list[str] = Field(
        description="A list of requirements an applicant needs to apply for the job"
    )
    date_posted: str = Field(
        default_factory=lambda: date.today().strftime("%d-%m-%Y"),
        description="The date this posting was made in dd-mm-YYYY format",
    )
    deadline: str = Field(
        default_factory=lambda: (date.today() + timedelta(days=30)).strftime(
            "%d-%m-%Y"
        ),
        description="The last date to apply in dd-mm-YYYY format",
    )
    notes: list[str] | None = Field(
        description="Additional notes while applying for the job. For example the application process, expected documents etc."
    )


class JobListings(BaseModel):
    jobs: list[Job] = Field(description="A list of jobs")


class Metadata(BaseModel):
    job_id: str = Field(description="Job's unique identifier")
    strengths: list[str] = Field(
        description="Specific ways the candidate's background matches this job"
    )
    gaps: list[str] = Field(
        description="Specific requirements the candidate's background does not clearly address, if any"
    )
    verdict: str = Field(
        description="One or two sentence recommendation, in plain language, with no numeric score or percentage"
    )


class MetadataList(BaseModel):
    data: list[Metadata] = Field(description="A list of job metadata")
