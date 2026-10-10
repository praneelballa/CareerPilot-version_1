import shutil
import uuid
import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from app.config import Settings, get_settings
from app.schemas.candidate import ResumeUploadResponse, ResumeAnalyzeRequest, CandidateProfile
from app.services.extractor import ResumeExtractorService
from app.agents.resume_parser import ResumeParserAgent

router = APIRouter()
resume_agent = ResumeParserAgent()


def get_paths(settings: Settings = Depends(get_settings)):
    upload_path = Path(settings.UPLOAD_DIR)
    processed_path = Path(settings.PROCESSED_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    processed_path.mkdir(parents=True, exist_ok=True)
    return upload_path, processed_path


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    upload_path, _ = get_paths(settings)
    
    # 1. Validate File Extension
    filename = file.filename or "resume.pdf"
    extension = Path(filename).suffix.lower()
    if extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{extension}'. Allowed: .pdf, .docx"
        )

    # 2. Check File Size Limit
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    candidate_id = str(uuid.uuid4())
    saved_file_name = f"{candidate_id}{extension}"
    destination = upload_path / saved_file_name

    with open(destination, "wb") as f:
        f.write(contents)

    # 3. Extract Raw Deterministic Text
    raw_text = ResumeExtractorService.extract_text(destination, extension)

    # 4. Save raw text for analyzer step
    text_cache_path = upload_path / f"{candidate_id}.txt"
    with open(text_cache_path, "w", encoding="utf-8") as f:
        f.write(raw_text)

    return ResumeUploadResponse(
        candidate_id=candidate_id,
        filename=filename,
        extracted_text_preview=raw_text[:350] + ("..." if len(raw_text) > 350 else ""),
        character_count=len(raw_text),
        message="Resume uploaded and text extracted deterministically. Ready for semantic analysis."
    )


@router.post("/analyze", response_model=CandidateProfile, status_code=status.HTTP_200_OK)
async def analyze_resume(
    payload: ResumeAnalyzeRequest,
    settings: Settings = Depends(get_settings)
):
    upload_path, processed_path = get_paths(settings)
    text_cache_path = upload_path / f"{payload.candidate_id}.txt"

    if not text_cache_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Uploaded resume session '{payload.candidate_id}' not found. Please upload first."
        )

    with open(text_cache_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Pass text to Gemini Agent
    profile = await resume_agent.parse_resume_text(
        candidate_id=payload.candidate_id,
        raw_text=raw_text
    )

    # Store normalized profile locally
    profile_out_path = processed_path / f"{payload.candidate_id}.json"
    with open(profile_out_path, "w", encoding="utf-8") as f:
        f.write(profile.model_dump_json(indent=2))

    return profile


@router.get("/candidate/{candidate_id}", response_model=CandidateProfile, status_code=status.HTTP_200_OK)
async def get_candidate_profile(
    candidate_id: str,
    settings: Settings = Depends(get_settings)
):
    _, processed_path = get_paths(settings)
    profile_path = processed_path / f"{candidate_id}.json"

    if not profile_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile for id '{candidate_id}' was not found. Please trigger analysis first."
        )

    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return CandidateProfile(**data)