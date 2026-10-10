import json
from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

from groq import AsyncGroq
from app.config import get_settings
from app.schemas.candidate import CandidateProfile
from app.schemas.job import Job
from app.schemas.matching import (
    MatchMetrics,
    AgentReasoningOutput,
    MatchingAnalysisResponse,
    SkillEvidence,
    SkillGapItem,
    RoadmapMilestone
)
from app.services.matcher import DeterministicMatcher

settings = get_settings()


class MatchingGraphState(TypedDict):
    profile: CandidateProfile
    job: Job
    metrics: Optional[MatchMetrics]
    matched_skills: List[str]
    missing_skills: List[str]
    reasoning: Optional[AgentReasoningOutput]
    final_response: Optional[MatchingAnalysisResponse]
    error: Optional[str]


async def calculate_deterministic_metrics_node(state: MatchingGraphState) -> Dict[str, Any]:
    try:
        metrics, matched, missing = DeterministicMatcher.compute_metrics(
            state["profile"], state["job"]
        )
        return {
            "metrics": metrics,
            "matched_skills": matched,
            "missing_skills": missing
        }
    except Exception as e:
        return {"error": f"Deterministic math failed: {str(e)}"}


def sanitize_reasoning_dict(data: dict) -> dict:
    if "compatibility_explanation" not in data:
        data["compatibility_explanation"] = data.get("explanation", "Match assessment completed.")
    if "evidence_breakdown" not in data or not isinstance(data["evidence_breakdown"], list):
        data["evidence_breakdown"] = []
    if "skill_gaps" not in data or not isinstance(data["skill_gaps"], list):
        data["skill_gaps"] = []
    if "career_roadmap" not in data or not isinstance(data["career_roadmap"], list):
        data["career_roadmap"] = []

    clean_evidence = []
    for item in data["evidence_breakdown"]:
        if isinstance(item, dict):
            if "skill" not in item:
                item["skill"] = item.get("requirement") or item.get("name") or "Required Skill"
            if "in_resume" not in item:
                item["in_resume"] = bool(item.get("evidence_quote"))
            clean_evidence.append(item)
    data["evidence_breakdown"] = clean_evidence

    clean_gaps = []
    for gap in data["skill_gaps"]:
        if isinstance(gap, dict):
            if "skill" not in gap:
                gap["skill"] = gap.get("requirement") or gap.get("name") or "Skill Gap"
            if "priority" not in gap:
                gap["priority"] = "important"
            if "current_gap" not in gap:
                gap["current_gap"] = gap.get("description", "Needs development")
            if "recommended_learning" not in gap:
                gap["recommended_learning"] = gap.get("suggestion", "Study official documentation and build a project.")
            clean_gaps.append(gap)
    data["skill_gaps"] = clean_gaps

    clean_roadmap = []
    for idx, step in enumerate(data["career_roadmap"]):
        if isinstance(step, dict):
            if "step" not in step:
                step["step"] = idx + 1
            if "title" not in step:
                step["title"] = f"Milestone {idx + 1}"
            if "focus_area" not in step:
                step["focus_area"] = "Core Competency"
            if "target_skills" not in step or not isinstance(step["target_skills"], list):
                step["target_skills"] = []
            if "practice_project" not in step:
                step["practice_project"] = "Build an end-to-end implementation project."
            if "recommended_resume_bullet" not in step:
                step["recommended_resume_bullet"] = f"Implemented {step.get('title', 'system feature')} using target architecture."
            clean_roadmap.append(step)
    data["career_roadmap"] = clean_roadmap

    return data


async def generate_agent_reasoning_node(state: MatchingGraphState) -> Dict[str, Any]:
    if state.get("error"):
        return {}

    if not settings.GROQ_API_KEY:
        return {"error": "GROQ_API_KEY missing. Cannot perform semantic analysis."}

    profile: CandidateProfile = state["profile"]
    job: Job = state["job"]
    metrics: MatchMetrics = state["metrics"]

    system_instruction = (
        "You are the Lead Career Matching Engineer at CareerPilotAI.\n"
        "Analyze candidate qualifications against job requirements.\n"
        "You MUST output pure, valid JSON with these EXACT keys:\n"
        "{\n"
        '  "compatibility_explanation": "string",\n'
        '  "evidence_breakdown": [{"skill": "string", "in_resume": true, "evidence_quote": "string", "job_requirement_context": "string"}],\n'
        '  "skill_gaps": [{"skill": "string", "priority": "critical", "current_gap": "string", "recommended_learning": "string"}],\n'
        '  "career_roadmap": [{"step": 1, "title": "string", "focus_area": "string", "target_skills": ["string"], "practice_project": "string", "recommended_resume_bullet": "string"}]\n'
        "}\n"
        "CRITICAL: Key name must be 'skill' (NOT 'requirement'). Keep response concise."
    )

    clean_desc = (job.description or "")[:1000]
    top_projects = [
        {"title": p.title, "tech": p.technologies[:4], "desc": (p.description or "")[:120]}
        for p in profile.projects[:3]
    ]

    user_prompt = f"""
Candidate: {profile.name}
Summary: {profile.summary}
Skills: {profile.skills.model_dump_json()}
Top Projects: {top_projects}

Job: {job.title} at {job.company} ({job.remote_type})
Description: {clean_desc}
Required Skills: {job.required_skills}

Metrics:
Similarity: {metrics.semantic_similarity}, Skill Coverage: {metrics.skill_coverage}
Matched: {state['matched_skills']}
Missing: {state['missing_skills']}

Provide concise JSON with max 3 evidence items, 2 skill gaps, and 3 roadmap milestones.
"""

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    try:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=900,
        )
        raw_data = json.loads(response.choices[0].message.content)
        sanitized = sanitize_reasoning_dict(raw_data)
        reasoning = AgentReasoningOutput(**sanitized)
        return {"reasoning": reasoning}
    except Exception as e:
        return {"error": f"Groq reasoning failed: {str(e)}"}


async def assemble_final_response_node(state: MatchingGraphState) -> Dict[str, Any]:
    if state.get("error"):
        return {}

    reasoning: AgentReasoningOutput = state["reasoning"]
    response = MatchingAnalysisResponse(
        candidate_id=state["profile"].candidate_id,
        job_id=state["job"].job_id,
        job_title=state["job"].title,
        company=state["job"].company,
        metrics=state["metrics"],
        compatibility_explanation=reasoning.compatibility_explanation,
        evidence_breakdown=reasoning.evidence_breakdown,
        skill_gaps=reasoning.skill_gaps,
        career_roadmap=reasoning.career_roadmap
    )
    return {"final_response": response}


def build_matching_graph():
    workflow = StateGraph(MatchingGraphState)
    workflow.add_node("calculate_math", calculate_deterministic_metrics_node)
    workflow.add_node("agent_reasoning", generate_agent_reasoning_node)
    workflow.add_node("assemble_response", assemble_final_response_node)

    workflow.add_edge(START, "calculate_math")
    workflow.add_edge("calculate_math", "agent_reasoning")
    workflow.add_edge("agent_reasoning", "assemble_response")
    workflow.add_edge("assemble_response", END)

    return workflow.compile()


matching_execution_graph = build_matching_graph()
# Backwards compatibility export
matching_agent_graph = matching_execution_graph