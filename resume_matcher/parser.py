"""Parsers that turn raw text into Candidate and JobDescription objects."""

from __future__ import annotations

from typing import List, Optional

from .file_handler import read_file
from .models import Candidate, JobDescription
from .skills import (
    SKILL_ALIASES,
    extract_education,
    extract_experience_years,
    extract_keywords,
    extract_name,
    extract_skills,
)


class ResumeParser:
    """Parse resume text into a Candidate."""

    def __init__(self, skill_aliases=None):
        self.skill_aliases = skill_aliases or SKILL_ALIASES

    def parse_text(self, text: str, source_path: str = "") -> Candidate:
        if not text or not text.strip():
            raise ValueError("Resume text is empty")
        name = extract_name(text)
        skills = extract_skills(text, self.skill_aliases)
        experience = extract_experience_years(text)
        education = extract_education(text)
        keywords = extract_keywords(text)
        return Candidate(
            name=name,
            source_path=source_path,
            raw_text=text,
            skills=skills,
            experience_years=experience,
            education=education,
            keywords=keywords,
        )

    def parse_file(self, path: str) -> Candidate:
        text = read_file(path)
        return self.parse_text(text, source_path=path)


class JobParser:
    """Parse job description text into a JobDescription."""

    def __init__(self, skill_aliases=None):
        self.skill_aliases = skill_aliases or SKILL_ALIASES

    def parse_text(
        self, text: str, source_path: str = "", title: Optional[str] = None
    ) -> JobDescription:
        if not text or not text.strip():
            raise ValueError("Job description text is empty")
        required = extract_skills(text, self.skill_aliases)
        required_skills, preferred_skills = self._split_required_preferred(text, required)
        experience = extract_experience_years(text)
        education = extract_education(text)
        job_title = title or self._extract_title(text)
        return JobDescription(
            title=job_title,
            source_path=source_path,
            raw_text=text,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            min_experience_years=experience,
            education_requirements=education,
        )

    def parse_file(self, path: str, title: Optional[str] = None) -> JobDescription:
        text = read_file(path)
        return self.parse_text(text, source_path=path, title=title)

    @staticmethod
    def _extract_title(text: str) -> str:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            low = line.lower()
            if any(tok in low for tok in ("job title", "position", "role", "title")):
                if ":" in line:
                    return line.split(":", 1)[1].strip() or line
                return line
            if len(line) <= 60:
                return line
        return "Untitled Job"

    @staticmethod
    def _split_required_preferred(text: str, all_skills: List[str]) -> tuple[List[str], List[str]]:
        required_section = ""
        preferred_section = ""
        lines = text.splitlines()
        current = None
        for line in lines:
            l = line.lower().strip()
            if "required" in l or "must have" in l or "mandatory" in l:
                current = "required"
                if ":" in line:
                    required_section += " " + line.split(":", 1)[1]
                continue
            if "preferred" in l or "nice to have" in l or "optional" in l or "bonus" in l:
                current = "preferred"
                if ":" in line:
                    preferred_section += " " + line.split(":", 1)[1]
                continue
            if current == "required":
                required_section += " " + line
            elif current == "preferred":
                preferred_section += " " + line

        if not required_section and not preferred_section:
            return sorted(set(all_skills)), []

        req_skills = extract_skills(required_section, SKILL_ALIASES) if required_section.strip() else []
        pref_skills = extract_skills(preferred_section, SKILL_ALIASES) if preferred_section.strip() else []
        leftover = [s for s in all_skills if s not in req_skills and s not in pref_skills]
        req_skills = sorted(set(req_skills) | set(leftover))
        return req_skills, sorted(set(pref_skills))
