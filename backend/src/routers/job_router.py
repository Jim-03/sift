from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_throttle import RateLimiter
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.config.logger import logger
from src.config.model import JobMetadataModel, JobModel
from src.dto.job_dto import (
    EmploymentType,
    FullJobDto,
    JobDataDto,
    JobReview,
    StatisticsDto,
)
from src.services.job_service import JobService
from src.services.ollama_service import Verdict

api_limit = RateLimiter(times=5, seconds=60, detail="Server under heavy load")
job_router = APIRouter(prefix="/jobs", tags=["Jobs"], dependencies=[Depends(api_limit)])


@job_router.patch(
    "/{job_id}", summary="Update job", response_model=FullJobDto, status_code=200
)
def update_job(
    job_id: UUID,
    read: bool | None = None,
    applied: bool | None = None,
    db: Session = Depends(get_db),
):
    """Partially update a job

    Args:
        job_id: Unique job identifier
        read: Update to read field
        applied: Update to applied field
        db: database dependency

    Returns:
        (FullJobDto): Newly updated job data

    """
    try:
        job = db.query(JobModel).filter(JobModel.id == job_id).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if read is not None:
            job.read = read
        if applied is not None:
            job.applied = applied

        db.commit()
        db.refresh(job)

        return job
    except Exception as e:
        db.rollback()
        logger.error(f"An error has occurred while updating a job: {e}")
        raise


@job_router.get(
    "/{job_id}/analysis",
    response_model=JobReview,
    status_code=200,
    summary="Get job analysis",
    description="Invoke Gemini to analyze job fitness against the user profile",
)
async def get_analysis(
    job_id: UUID, db: Session = Depends(get_db), service: JobService = Depends()
):
    """Generate job analysis

    Args:
        job_id: Job unique identifier
        db: Database session
        service: Job service

    Returns:
         (JobReview): Generated job match evaluation
    """
    job = db.query(JobModel).filter(JobModel.id == job_id).one()

    if not job:
        raise HTTPException(status_code=404, detail="Job Not found")

    if job.job_metadata:
        return job.job_metadata

    metadata = await service.evaluate_jobs([job])

    return metadata[0]


@job_router.get(
    "", summary="Get jobs", response_model=list[JobDataDto], status_code=200
)
async def get_jobs(
    search_query: str | None = None,
    limit: int = 10,
    page: int = 0,
    job_type: EmploymentType | None = None,
    read: bool | None = None,
    applied: bool | None = None,
    db: Session = Depends(get_db),
):
    """Retrieve jobs

    Args:
        job_type: Type of job to fetch
        read: View status
        applied: Application status
        search_query: Company name/job title to fetch
        limit: Number of records to fetch in a page
        page: Page number. 0-indexed
        db: Database dependency

    Returns:
        (list[JobDataDto]): List of jobs

    """

    stmt = db.query(JobModel)

    where = []

    if search_query:
        where.append(
            or_(
                JobModel.title.ilike(f"%{search_query}%"),
                JobModel.company.ilike(f"%{search_query}%"),
            )
        )

    if job_type:
        where.append(and_(JobModel.employment_type == job_type))

    if read is not None:
        where.append(and_(JobModel.read == read))

    if applied is not None:
        where.append(and_(JobModel.applied == applied))

    if len(where) != 0:
        stmt = stmt.where(*where)

    stmt = stmt.order_by(JobModel.created_at.desc()).limit(limit).offset(page * limit)

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
        func.sum(case((JobModel.applied, 1), else_=0)).label("applied"),
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
        .filter(JobMetadataModel.verdict == Verdict.STRONG)
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
