"""Data models for candidates, job descriptions, and match results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Candidate:
    """Represents a parsed candidate resume."""

    name: str
    source_path: str
    raw_text: str
    skills: List[str] = field(default_factory=list)
    experience_years: float = 0.0
    education: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "source_path": self.source_path,
            "skills": list(self.skills),
            "experience_years": self.experience_years,
            "education": list(self.education),
            "keywords": list(self.keywords),
        }


@dataclass
class JobDescription:
    """Represents a parsed job description."""

    title: str
    source_path: str
    raw_text: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    min_experience_years: float = 0.0
    education_requirements: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "source_path": self.source_path,
            "required_skills": list(self.required_skills),
            "preferred_skills": list(self.preferred_skills),
            "min_experience_years": self.min_experience_years,
            "education_requirements": list(self.education_requirements),
        }


@dataclass
class MatchResult:
    """Result of matching one candidate against a job description."""

    candidate: Candidate
    job: JobDescription
    score: float = 0.0
    skill_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    extra_skills: List[str] = field(default_factory=list)
    rank: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "candidate": self.candidate.name,
            "score": round(self.score, 2),
            "skill_score": round(self.skill_score, 2),
            "experience_score": round(self.experience_score, 2),
            "education_score": round(self.education_score, 2),
            "matched_skills": list(self.matched_skills),
            "missing_skills": list(self.missing_skills),
            "extra_skills": list(self.extra_skills),
        }
