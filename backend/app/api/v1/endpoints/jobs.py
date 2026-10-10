from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.schemas.job import Job, JobSearchFilter, JobSearchResponse
from app.services.job_discovery import JobDiscoveryService
from app.services.job_repository import JobRepository

router = APIRouter()
discovery_service = JobDiscoveryService()
job_repo = JobRepository()


@router.post("/search", response_model=JobSearchResponse, status_code=status.HTTP_200_OK)
async def search_jobs(payload: JobSearchFilter):
    try:
        response = await discovery_service.discover_jobs(payload)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job discovery pipeline failed: {str(e)}"
        )


@router.get("/", response_model=List[Job], status_code=status.HTTP_200_OK)
async def list_stored_jobs(limit: int = Query(50, ge=1, le=100)):
    return await job_repo.list_jobs(limit=limit)


@router.get("/{job_id}", response_model=Job, status_code=status.HTTP_200_OK)
async def get_job_by_id(job_id: str):
    job = await job_repo.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found in local index."
        )
    return job