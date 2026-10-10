import aiosqlite
import json
from pathlib import Path
from typing import List, Optional
from app.schemas.job import Job
from app.schemas.company import CompanyResearch
from app.schemas.application import ApplicationDraft, ResumeVersion, ResumeSuggestion, AuditLogEntry

DB_PATH = Path("../data/jobs/careerpilot_jobs.db")


class JobRepository:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(DB_PATH)

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    remote_type TEXT,
                    employment_type TEXT,
                    description TEXT,
                    required_skills TEXT,
                    preferred_skills TEXT,
                    salary TEXT,
                    posted_date TEXT,
                    application_url TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    retrieved_at TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS company_research (
                    company_name TEXT PRIMARY KEY,
                    official_domain TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    retrieved_at TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS resume_versions (
                    version_id TEXT PRIMARY KEY,
                    candidate_id TEXT NOT NULL,
                    parent_version_id TEXT,
                    job_id TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    applied_suggestion_ids TEXT NOT NULL,
                    tailored_summary TEXT NOT NULL,
                    modified_bullets TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS application_drafts (
                    id TEXT PRIMARY KEY,
                    candidate_id TEXT NOT NULL,
                    job_id TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    resume_version_id TEXT,
                    recipient TEXT,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    attachment_path TEXT,
                    gmail_message_id TEXT,
                    sent_at TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS resume_suggestions_cache (
                    cache_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    details TEXT
                )
            """)

            cursor = await db.execute("PRAGMA table_info(application_drafts)")
            columns = [row[1] for row in await cursor.fetchall()]
            if "gmail_message_id" not in columns:
                await db.execute("ALTER TABLE application_drafts ADD COLUMN gmail_message_id TEXT")
            if "sent_at" not in columns:
                await db.execute("ALTER TABLE application_drafts ADD COLUMN sent_at TEXT")
                
            await db.commit()

    async def record_audit_log(self, application_id: str, action: str, details: Optional[str] = None):
        await self.init_db()
        import datetime
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO audit_logs (application_id, action, timestamp, details) VALUES (?, ?, ?, ?)",
                (application_id, action, ts, details)
            )
            await db.commit()

    async def get_audit_logs(self, application_id: str) -> List[AuditLogEntry]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM audit_logs WHERE application_id = ? ORDER BY id ASC",
                (application_id,)
            )
            rows = await cursor.fetchall()
            return [
                AuditLogEntry(
                    id=row["id"],
                    application_id=row["application_id"],
                    action=row["action"],
                    timestamp=row["timestamp"],
                    details=row["details"]
                )
                for row in rows
            ]

    async def save_application(self, draft: ApplicationDraft):
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO application_drafts (
                    id, candidate_id, job_id, company_name, resume_version_id,
                    recipient, subject, body, attachment_path, gmail_message_id,
                    sent_at, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                draft.id, draft.candidate_id, draft.job_id, draft.company_name,
                draft.resume_version_id, draft.recipient, draft.subject, draft.body,
                draft.attachment_path, draft.gmail_message_id, draft.sent_at,
                draft.status.value, draft.created_at, draft.updated_at
            ))
            await db.commit()

    async def get_application(self, app_id: str) -> Optional[ApplicationDraft]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM application_drafts WHERE id = ?", (app_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            return ApplicationDraft(
                id=row["id"],
                candidate_id=row["candidate_id"],
                job_id=row["job_id"],
                company_name=row["company_name"],
                resume_version_id=row["resume_version_id"],
                recipient=row["recipient"],
                subject=row["subject"],
                body=row["body"],
                attachment_path=row["attachment_path"],
                gmail_message_id=row["gmail_message_id"],
                sent_at=row["sent_at"],
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )

    async def list_applications(self, limit: int = 50) -> List[ApplicationDraft]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM application_drafts ORDER BY updated_at DESC LIMIT ?", (limit,))
            rows = await cursor.fetchall()
            return [
                ApplicationDraft(
                    id=row["id"],
                    candidate_id=row["candidate_id"],
                    job_id=row["job_id"],
                    company_name=row["company_name"],
                    resume_version_id=row["resume_version_id"],
                    recipient=row["recipient"],
                    subject=row["subject"],
                    body=row["body"],
                    attachment_path=row["attachment_path"],
                    gmail_message_id=row["gmail_message_id"],
                    sent_at=row["sent_at"],
                    status=row["status"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                for row in rows
            ]

    # Preserved methods
    async def save_suggestions_cache(self, candidate_id: str, job_id: str, suggestions: List[ResumeSuggestion]):
        await self.init_db()
        key = f"{candidate_id}::{job_id}"
        payload = json.dumps([s.model_dump() for s in suggestions])
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO resume_suggestions_cache (cache_key, payload) VALUES (?, ?)", (key, payload))
            await db.commit()

    async def get_suggestions_cache(self, candidate_id: str, job_id: str) -> Optional[List[ResumeSuggestion]]:
        await self.init_db()
        key = f"{candidate_id}::{job_id}"
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT payload FROM resume_suggestions_cache WHERE cache_key = ?", (key,))
            row = await cursor.fetchone()
            if not row:
                return None
            return [ResumeSuggestion(**s) for s in json.loads(row["payload"])]

    async def save_resume_version(self, version: ResumeVersion):
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO resume_versions (
                    version_id, candidate_id, parent_version_id, job_id,
                    version_number, applied_suggestion_ids, tailored_summary, modified_bullets, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version.version_id, version.candidate_id, version.parent_version_id, version.job_id,
                version.version_number, json.dumps(version.applied_suggestion_ids), version.tailored_summary,
                json.dumps(version.modified_bullets), version.created_at
            ))
            await db.commit()

    async def get_resume_version(self, version_id: str) -> Optional[ResumeVersion]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM resume_versions WHERE version_id = ?", (version_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            return ResumeVersion(
                version_id=row["version_id"],
                candidate_id=row["candidate_id"],
                parent_version_id=row["parent_version_id"],
                job_id=row["job_id"],
                version_number=row["version_number"],
                applied_suggestion_ids=json.loads(row["applied_suggestion_ids"]),
                tailored_summary=row["tailored_summary"],
                modified_bullets=json.loads(row["modified_bullets"]),
                created_at=row["created_at"]
            )

    async def save_company_research(self, research: CompanyResearch):
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO company_research (company_name, official_domain, payload, retrieved_at) VALUES (?, ?, ?, ?)",
                (research.company_name.lower().strip(), research.official_domain, research.model_dump_json(), research.retrieved_at)
            )
            await db.commit()

    async def get_company_research(self, company_name: str) -> Optional[CompanyResearch]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT payload FROM company_research WHERE company_name = ?", (company_name.lower().strip(),))
            row = await cursor.fetchone()
            if not row:
                return None
            return CompanyResearch(**json.loads(row["payload"]))

    async def get_job_by_id(self, job_id: str) -> Optional[Job]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            return Job(
                job_id=row["job_id"],
                source=row["source"],
                title=row["title"],
                company=row["company"],
                location=row["location"],
                remote_type=row["remote_type"],
                employment_type=row["employment_type"],
                description=row["description"],
                required_skills=json.loads(row["required_skills"]),
                preferred_skills=json.loads(row["preferred_skills"]),
                salary=row["salary"],
                posted_date=row["posted_date"],
                application_url=row["application_url"],
                source_url=row["source_url"],
                retrieved_at=row["retrieved_at"]
            )

    async def save_jobs(self, jobs: List[Job]) -> int:
        await self.init_db()
        inserted_count = 0
        async with aiosqlite.connect(self.db_path) as db:
            for job in jobs:
                try:
                    await db.execute("""
                        INSERT OR REPLACE INTO jobs (
                            job_id, source, title, company, location, remote_type,
                            employment_type, description, required_skills, preferred_skills,
                            salary, posted_date, application_url, source_url, retrieved_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        job.job_id, job.source, job.title, job.company, job.location,
                        job.remote_type, job.employment_type, job.description,
                        json.dumps(job.required_skills), json.dumps(job.preferred_skills),
                        job.salary, job.posted_date, job.application_url, job.source_url, job.retrieved_at
                    ))
                    inserted_count += 1
                except Exception:
                    continue
            await db.commit()
        return inserted_count

    async def list_jobs(self, limit: int = 50) -> List[Job]:
        await self.init_db()
        jobs: List[Job] = []
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM jobs ORDER BY retrieved_at DESC LIMIT ?", (limit,))
            rows = await cursor.fetchall()
            for row in rows:
                jobs.append(Job(
                    job_id=row["job_id"],
                    source=row["source"],
                    title=row["title"],
                    company=row["company"],
                    location=row["location"],
                    remote_type=row["remote_type"],
                    employment_type=row["employment_type"],
                    description=row["description"],
                    required_skills=json.loads(row["required_skills"]),
                    preferred_skills=json.loads(row["preferred_skills"]),
                    salary=row["salary"],
                    posted_date=row["posted_date"],
                    application_url=row["application_url"],
                    source_url=row["source_url"],
                    retrieved_at=row["retrieved_at"]
                ))
        return jobs