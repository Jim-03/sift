from pydantic import BaseModel


class Company(BaseModel):
    name: str
    career_link: str
    link_container: str
    link_tag: str
    job_container: str


class CompaniesList(BaseModel):
    companies: list[Company]
