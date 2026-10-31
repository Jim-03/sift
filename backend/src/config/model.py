from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import UUID, Column, Enum, LargeBinary, String
from sqlalchemy.orm import declarative_base

from src.dto.job_dto import EmploymentType, ExperienceLevel

Base = declarative_base()


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String)
    level = Column(Enum(ExperienceLevel))
    duration = Column(Enum(EmploymentType))
    description = Column(String)
    responsibilities = Column(LargeBinary)
    requirements = Column(LargeBinary, nullable=False)
    benefits = Column(LargeBinary)
    salary = Column(String)
    deadline = Column(
        String,
        default=lambda: (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y"),
    )
