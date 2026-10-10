import re
from typing import Dict, List
from app.schemas.candidate import SkillCategories


CANONICAL_SKILL_MAP: Dict[str, str] = {
    # Languages
    "python3": "Python",
    "python 3": "Python",
    "python programming": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "golang": "Go",
    "c++": "C++",
    "cpp": "C++",
    
    # Frameworks & Libraries
    "react.js": "React",
    "reactjs": "React",
    "react native": "React Native",
    "vue.js": "Vue",
    "vuejs": "Vue",
    "fast-api": "FastAPI",
    "fastapi": "FastAPI",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    
    # Cloud & DB
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "amazon web services": "AWS",
    "aws": "AWS",
    "google cloud platform": "GCP",
    "gcp": "GCP",
    "docker containers": "Docker",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    
    # AI & ML
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "large language models": "LLMs",
    "llm": "LLMs",
    "llms": "LLMs",
    "langchain": "LangChain",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow"
}


class SkillNormalizer:
    @staticmethod
    def normalize_single_skill(raw_skill: str) -> str:
        clean = raw_skill.strip()
        lookup = clean.lower()
        return CANONICAL_SKILL_MAP.get(lookup, clean)

    @classmethod
    def normalize_skills(cls, skills: SkillCategories) -> SkillCategories:
        def clean_category(skill_list: List[str]) -> List[str]:
            seen = set()
            normalized = []
            for item in skill_list:
                canonical = cls.normalize_single_skill(item)
                if canonical.lower() not in seen and len(canonical) > 0:
                    seen.add(canonical.lower())
                    normalized.append(canonical)
            return normalized

        return SkillCategories(
            programming_languages=clean_category(skills.programming_languages),
            frameworks=clean_category(skills.frameworks),
            libraries=clean_category(skills.libraries),
            databases=clean_category(skills.databases),
            cloud_and_tools=clean_category(skills.cloud_and_tools),
            ai_and_ml=clean_category(skills.ai_and_ml),
            soft_skills=clean_category(skills.soft_skills)
        )