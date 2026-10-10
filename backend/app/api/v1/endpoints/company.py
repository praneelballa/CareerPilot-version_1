from fastapi import APIRouter, HTTPException, status
from app.schemas.company import CompanyResearch, CompanyResearchRequest
from app.agents.company_research_graph import company_research_subgraph
from app.services.job_repository import JobRepository

router = APIRouter()
repo = JobRepository()


@router.post("/research", response_model=CompanyResearch, status_code=status.HTTP_200_OK)
async def research_company(payload: CompanyResearchRequest):
    """
    Executes targeted, compliant research on the official company domain.
    """
    # 1. Check local cache
    job = await repo.get_job_by_id(payload.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{payload.job_id}' not found."
        )

    cached = await repo.get_company_research(job.company)
    if cached:
        return cached

    # 2. Invoke LangGraph Subgraph
    initial_state = {
        "job_id": payload.job_id,
        "job": None,
        "domain_info": None,
        "raw_pages": {},
        "research": None,
        "error": None
    }

    final_state = await company_research_subgraph.ainvoke(initial_state)

    if final_state.get("error"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=final_state["error"]
        )

    research = final_state["research"]
    await repo.save_company_research(research)
    return research


@router.get("/{company_name}/research", response_model=CompanyResearch, status_code=status.HTTP_200_OK)
async def get_stored_research(company_name: str):
    cached = await repo.get_company_research(company_name)
    if not cached:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No research records found for '{company_name}'."
        )
    return cached