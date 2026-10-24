"""Skill database and text extraction helpers."""

from __future__ import annotations

import re
from typing import Dict, List, Set

SKILL_ALIASES: Dict[str, List[str]] = {
    "python": ["python", "py"],
    "java": ["java"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", "c sharp"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "tsql"],
    "nosql": ["nosql", "mongodb", "mongo", "redis", "cassandra", "dynamodb"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react", "reactjs", "react.js"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vuejs", "vue.js"],
    "node.js": ["node.js", "nodejs", "node"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "fast api"],
    "spring": ["spring", "spring boot"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "nlp": ["nlp", "natural language processing"],
    "data analysis": ["data analysis", "data analytics"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "git": ["git", "github", "gitlab", "version control"],
    "linux": ["linux", "unix"],
    "rest api": ["rest", "rest api", "restful"],
    "graphql": ["graphql"],
    "agile": ["agile", "scrum"],
    "testing": ["testing", "unit testing", "pytest", "junit"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
    "communication": ["communication", "presentation"],
    "leadership": ["leadership", "team lead", "management"],
}

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "doctorate", "b.sc", "m.sc", "b.tech",
    "m.tech", "mba", "b.e", "m.e", "associate", "diploma", "degree",
]

EXPERIENCE_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+of\s+experience",
    r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",
    r"(\d+(?:\.\d+)?)\s*\+?\s*yrs?\s+of\s+experience",
    r"(\d+(?:\.\d+)?)\s*years?\s+experience",
]


def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(text: str, skill_aliases: Dict[str, List[str]] | None = None) -> List[str]:
    """Return a sorted list of canonical skills found in text."""
    aliases = skill_aliases or SKILL_ALIASES
    normalized = normalize_text(text)
    found: Set[str] = set()
    for canonical, alias_list in aliases.items():
        for alias in alias_list:
            pattern = r"(?<![a-z0-9+#.])" + re.escape(alias.lower()) + r"(?![a-z0-9+#.])"
            if re.search(pattern, normalized):
                found.add(canonical)
                break
    return sorted(found)


def extract_experience_years(text: str) -> float:
    """Best-effort extraction of years of experience from text."""
    normalized = normalize_text(text)
    best = 0.0
    for pattern in EXPERIENCE_PATTERNS:
        for match in re.finditer(pattern, normalized):
            try:
                value = float(match.group(1))
                if value > best:
                    best = value
            except (ValueError, IndexError):
                continue
    if best == 0.0:
        for match in re.finditer(r"(\d+(?:\.\d+)?)\s*years?", normalized):
            try:
                value = float(match.group(1))
                if 0 < value <= 50 and value > best:
                    best = value
            except ValueError:
                continue
    return best


def extract_education(text: str) -> List[str]:
    """Extract education-related phrases from text."""
    normalized = normalize_text(text)
    found: Set[str] = set()
    for keyword in EDUCATION_KEYWORDS:
        if keyword in normalized:
            found.add(keyword)
    lines = text.splitlines()
    for line in lines:
        low = line.lower()
        if any(k in low for k in EDUCATION_KEYWORDS):
            cleaned = line.strip()
            if cleaned and len(cleaned) < 200:
                found.add(cleaned)
    return sorted(found)


def extract_name(text: str) -> str:
    """Heuristic: first non-empty line that looks like a name."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        low = line.lower()
        if any(tok in low for tok in ("resume", "curriculum", "vitae", "objective", "summary")):
            continue
        if len(line) > 60:
            continue
        if re.fullmatch(r"[A-Za-z][A-Za-z .'-]{1,58}", line) and len(line.split()) <= 5:
            return line
        return line[:60]
    return "Unknown Candidate"


def extract_keywords(text: str, top_n: int = 20) -> List[str]:
    """Extract simple keyword tokens (alphanumeric) excluding stopwords."""
    stopwords = {
        "the", "and", "or", "of", "to", "in", "for", "with", "on", "a", "an",
        "is", "are", "was", "were", "be", "been", "being", "as", "at", "by",
        "from", "that", "this", "it", "its", "we", "you", "he", "she", "they",
        "i", "me", "my", "our", "your", "their", "have", "has", "had", "do",
        "does", "did", "will", "would", "can", "could", "should", "may", "might",
    }
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", text.lower())
    freq: Dict[str, int] = {}
    for tok in tokens:
        if tok in stopwords:
            continue
        freq[tok] = freq.get(tok, 0) + 1
    sorted_tokens = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    return [t for t, _ in sorted_tokens[:top_n]]
