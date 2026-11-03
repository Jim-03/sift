from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import ARRAY, UUID, Column, Enum, String
from sqlalchemy.orm import declarative_base

from src.dto.job_dto import EmploymentType, ExperienceLevel

Base = declarative_base()


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String)
    company = Column(String)
    experience_level = Column(Enum(ExperienceLevel))
    employment_type = Column(Enum(EmploymentType))
    description = Column(String)
    responsibilities = Column(ARRAY(String))
    requirements = Column(ARRAY(String), nullable=False)
    benefits = Column(ARRAY(String))
    salary = Column(String)
    deadline = Column(
        String,
        default=lambda: (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y"),
    )
