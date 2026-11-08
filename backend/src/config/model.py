from datetime import datetime, timedelta
from uuid import uuid4

import pytz
from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    UUID,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

from src.dto.job_dto import EmploymentType, ExperienceLevel
from src.services.ollama_service import Verdict

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
    applied = Column(Boolean, server_default="false", nullable=False)
    read = Column(Boolean, server_default="false", nullable=False)
    deadline = Column(
        String,
        default=lambda: (
            datetime.now(pytz.timezone("Africa/Nairobi")) + timedelta(days=7)
        ).strftime("%d-%m-%Y"),
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(pytz.timezone("Africa/Nairobi")),
    )

    job_metadata = relationship("JobMetadataModel", back_populates="job", uselist=False)


class JobMetadataModel(Base):
    __tablename__ = "job_metadata"

    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), primary_key=True)
    reasoning = Column(String)
    matches = Column(ARRAY(String))
    gaps = Column(ARRAY(String))
    partial = Column(ARRAY(String))
    verdict = Column(Enum(Verdict))
    created_at = Column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(pytz.timezone("Africa/Nairobi")),
    )

    job = relationship("JobModel", back_populates="job_metadata")
