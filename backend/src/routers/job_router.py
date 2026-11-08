from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import ColumnElement, case, func, or_
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.config.model import JobMetadataModel, JobModel
from src.dto.job_dto import FullJobDto, JobDataDto, StatisticsDto
from src.services.ollama_service import Verdict

job_router = APIRouter(prefix="/jobs", tags=["Jobs"])


@job_router.get(
    "", summary="Get jobs", response_model=list[JobDataDto], status_code=200
)
async def get_jobs(
    title: str | None = None,
    company: str | None = None,
    limit: int = 10,
    page: int = 0,
    db: Session = Depends(get_db),
):
    """Retrieve jobs

    Args:
        title: The name of the position to fetch
        company: Company name
        limit: Number of records to fetch in a page
        page: Page number. 0-indexed
        db: Database dependency

    Returns:
        (list[JobDataDto]): List of jobs

    """
    where: ColumnElement[bool] = []

    if company:
        where.append(JobModel.company.ilike(company))
    if title:
        where.append(JobModel.title.ilike(title))
    stmt = (
        db.query(JobModel)
        .order_by(JobModel.created_at)
        .limit(limit)
        .offset(limit * page)
    )

    if where:
        stmt.where(where)

    jobs = stmt.all()

    if len(jobs) == 0:
        raise HTTPException(status_code=404, detail="No jobs at the moment")

    return jobs


@job_router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)) -> StatisticsDto:
    """Retrieve home page statistics

    Args:
        db: Database dependency

    Returns:
        (StatisticsDto): Home page statistics

    """
    job_stats = db.query(
        func.count(JobModel.id).label("total"),
        func.sum(case((JobModel.applied == True, 1), else_=0)).label("applied"),
    ).one()

    job_count = job_stats.total
    applied = job_stats.applied or 0

    best_match_count = (
        db.query(JobMetadataModel)
        .filter(JobMetadataModel.verdict == Verdict.STRONG)
        .count()
    )

    best_jobs = (
        db.query(JobModel)
        .join(JobMetadataModel, JobModel.id == JobMetadataModel.job_id)
        .order_by(JobMetadataModel.created_at)
        .limit(5)
        .all()
    )

    recent_jobs = db.query(JobModel).order_by(JobModel.created_at).limit(5).all()

    return StatisticsDto(
        total_jobs=job_count,
        total_matches=best_match_count,
        applied=applied,
        best_match_jobs=best_jobs,
        recent_jobs=recent_jobs,
    )


@job_router.get(
    "/best",
    summary="Get best matching jobs",
    description="Get jobs ranked as strong/good match",
    response_model=list[FullJobDto],
    status_code=200,
)
def get_best_jobs(db: Session = Depends(get_db)):
    """Get best matching jobs

    Args:
        db: Database dependency

    Returns:
        (list[FullJobDto]): A list of jobs ranked as strong/good match

    """
    jobs = (
        db.query(JobModel)
        .join(JobMetadataModel, JobModel.id == JobMetadataModel.job_id)
        .where(
            or_(
                JobMetadataModel.verdict == Verdict.STRONG,
                JobMetadataModel.verdict == Verdict.GOOD,
            )
        )
        .order_by(JobModel.created_at)
        .all()
    )

    if not jobs:
        raise HTTPException(
            status_code=404, detail="No best matching jobs found at the moment"
        )

    return jobs


@job_router.get(
    "/{job_id}",
    response_model=FullJobDto,
    summary="Get job details",
    description="Retrieve a job's full description including review",
    status_code=200,
)
async def get_job(job_id: UUID, db: Session = Depends(get_db)):
    """Get job details

    Args:
        job_id: Unique job identifier
        db: Database dependency

    Returns:
        (FullJobDto): Job details together with its review
    """
    job = db.query(JobModel).filter(JobModel.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job
