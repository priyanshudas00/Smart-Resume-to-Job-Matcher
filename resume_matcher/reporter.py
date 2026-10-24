"""Format match results for console or file output."""

from __future__ import annotations

from typing import List

from .models import MatchResult


def format_result_table(results: List[MatchResult], top_n: int | None = None) -> str:
    if top_n is not None:
        results = results[:top_n]
    lines = []
    header = f"{'Rank':<5}{'Candidate':<28}{'Score':<8}{'Skill':<8}{'Exp':<8}{'Edu':<8}"
    lines.append(header)
    lines.append("-" * len(header))
    for r in results:
        lines.append(
            f"{r.rank:<5}{r.candidate.name[:26]:<28}{r.score:<8}{r.skill_score:<8}"
            f"{r.experience_score:<8}{r.education_score:<8}"
        )
    return "\n".join(lines)


def format_detailed(results: List[MatchResult]) -> str:
    blocks = []
    for r in results:
        block = []
        block.append(f"Rank {r.rank}: {r.candidate.name}  (Score: {r.score}/100)")
        block.append(
            f"  Skills: {r.skill_score}/100 | Experience: {r.experience_score}/100 | Education: {r.education_score}/100"
        )
        block.append(f"  Matched skills: {', '.join(r.matched_skills) if r.matched_skills else 'None'}")
        block.append(f"  Missing skills: {', '.join(r.missing_skills) if r.missing_skills else 'None'}")
        if r.extra_skills:
            block.append(f"  Extra skills: {', '.join(r.extra_skills)}")
        block.append(
            f"  Experience (years): {r.candidate.experience_years} (required {r.job.min_experience_years})"
        )
        blocks.append("\n".join(block))
    return "\n\n".join(blocks)


def write_report(path: str, results: List[MatchResult], title: str = "Resume Match Report") -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(f"{title}\n")
        handle.write("=" * len(title) + "\n\n")
        handle.write(format_result_table(results) + "\n\n")
        handle.write(format_detailed(results) + "\n")
