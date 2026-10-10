from fastapi import APIRouter, HTTPException, status
from app.schemas.matching import MatchingRequest, JobMatchAnalysis
from app.agents.matching_graph import matching_agent_graph

router = APIRouter()


@router.post("/analyze", response_model=JobMatchAnalysis, status_code=status.HTTP_200_OK)
async def analyze_match(payload: MatchingRequest):
    initial_state = {
        "candidate_id": payload.candidate_id,
        "job_id": payload.job_id,
        "profile": None,
        "job": None,
        "metrics": None,
        "matched_skills": [],
        "missing_skills": [],
        "reasoning": None,
        "final_analysis": None,
        "error": None
    }

    # Execute LangGraph state machine
    final_state = await matching_agent_graph.ainvoke(initial_state)

    if final_state.get("error"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=final_state["error"]
        )

    return final_state["final_analysis"]