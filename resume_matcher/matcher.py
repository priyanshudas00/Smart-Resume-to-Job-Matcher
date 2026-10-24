"""Orchestrate parsing, scoring, and ranking of candidates."""

from __future__ import annotations

from typing import Iterable, List

from .file_handler import collect_resume_files
from .models import Candidate, JobDescription, MatchResult
from .parser import JobParser, ResumeParser
from .scorer import Scorer


class Matcher:
    """High-level matcher: parse files, score, and rank candidates."""

    def __init__(self, scorer: Scorer | None = None, skill_aliases=None):
        self.scorer = scorer or Scorer()
        self.resume_parser = ResumeParser(skill_aliases)
        self.job_parser = JobParser(skill_aliases)

    def match_candidate(self, candidate: Candidate, job: JobDescription) -> MatchResult:
        return self.scorer.score(candidate, job)

    def match_candidates(self, candidates: Iterable[Candidate], job: JobDescription) -> List[MatchResult]:
        results = [self.scorer.score(c, job) for c in candidates]
        results.sort(key=lambda r: r.score, reverse=True)
        for idx, result in enumerate(results, start=1):
            result.rank = idx
        return results

    def match_from_paths(self, resume_paths: Iterable[str], job_path: str) -> List[MatchResult]:
        job = self.job_parser.parse_file(job_path)
        candidates = [self.resume_parser.parse_file(p) for p in resume_paths]
        return self.match_candidates(candidates, job)

    def match_from_directory(self, directory: str, job_path: str) -> List[MatchResult]:
        files = collect_resume_files(directory)
        if not files:
            raise FileNotFoundError(f"No supported resume files found in {directory}")
        return self.match_from_paths([str(f) for f in files], job_path)

    def match_texts(
        self,
        resume_texts: Iterable[str],
        job_text: str,
        names: Iterable[str] | None = None,
    ) -> List[MatchResult]:
        resume_texts = list(resume_texts)
        name_list = list(names) if names is not None else []
        candidates = []
        for i, text in enumerate(resume_texts):
            c = self.resume_parser.parse_text(text, source_path=f"inline:{i}")
            if i < len(name_list):
                c.name = name_list[i]
            candidates.append(c)
        job = self.job_parser.parse_text(job_text, source_path="inline:job")
        return self.match_candidates(candidates, job)
