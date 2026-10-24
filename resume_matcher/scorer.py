"""Scoring engine for candidate-job fit."""

from __future__ import annotations

from .models import Candidate, JobDescription, MatchResult
from .skills import normalize_text


class Scorer:
    """Compute a fit score between a candidate and a job description."""

    def __init__(
        self,
        skill_weight: float = 0.5,
        experience_weight: float = 0.3,
        education_weight: float = 0.2,
        preferred_bonus: float = 0.1,
    ):
        total = skill_weight + experience_weight + education_weight
        if abs(total - 1.0) > 1e-9:
            raise ValueError("Weights must sum to 1.0")
        self.skill_weight = skill_weight
        self.experience_weight = experience_weight
        self.education_weight = education_weight
        self.preferred_bonus = preferred_bonus

    def score(self, candidate: Candidate, job: JobDescription) -> MatchResult:
        cand_skills = {s.lower() for s in candidate.skills}
        req_skills = {s.lower() for s in job.required_skills}
        pref_skills = {s.lower() for s in job.preferred_skills}

        matched_required = sorted(req_skills & cand_skills)
        missing_required = sorted(req_skills - cand_skills)
        matched_preferred = sorted(pref_skills & cand_skills)
        extra = sorted(cand_skills - req_skills - pref_skills)

        if req_skills:
            skill_core = len(matched_required) / len(req_skills)
        else:
            skill_core = 1.0
        preferred_ratio = (len(matched_preferred) / len(pref_skills)) if pref_skills else 0.0
        skill_score = skill_core + preferred_ratio * self.preferred_bonus
        skill_score = min(skill_score, 1.0)

        if job.min_experience_years > 0:
            experience_score = min(candidate.experience_years / job.min_experience_years, 1.0)
        else:
            experience_score = 1.0 if candidate.experience_years > 0 else 0.5

        education_score = self._education_score(candidate, job)

        total = (
            skill_score * self.skill_weight
            + experience_score * self.experience_weight
            + education_score * self.education_weight
        ) * 100.0

        matched_all = sorted((req_skills | pref_skills) & cand_skills)
        return MatchResult(
            candidate=candidate,
            job=job,
            score=round(total, 2),
            skill_score=round(skill_score * 100, 2),
            experience_score=round(experience_score * 100, 2),
            education_score=round(education_score * 100, 2),
            matched_skills=matched_all,
            missing_skills=missing_required,
            extra_skills=extra,
        )

    @staticmethod
    def _education_score(candidate: Candidate, job: JobDescription) -> float:
        if not job.education_requirements:
            return 1.0 if candidate.education else 0.5
        cand_edu_text = normalize_text(" ".join(candidate.education))
        req_edu_text = normalize_text(" ".join(job.education_requirements))
        req_tokens = set(req_edu_text.split())
        cand_tokens = set(cand_edu_text.split())
        if not req_tokens:
            return 0.5
        overlap = len(req_tokens & cand_tokens) / len(req_tokens)
        if any(k in cand_edu_text for k in ("bachelor", "master", "phd", "mba", "degree")):
            overlap = max(overlap, 0.6)
        return min(overlap, 1.0)
