"""Smart Resume-to-Job Matcher package."""

from .matcher import Matcher
from .models import Candidate, JobDescription, MatchResult
from .scorer import Scorer

__all__ = ["Matcher", "Candidate", "JobDescription", "MatchResult", "Scorer"]
__version__ = "1.0.0"
