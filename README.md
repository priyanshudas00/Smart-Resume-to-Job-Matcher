# Smart Resume-to-Job Matcher

A production-ready Python web application that parses resumes and job descriptions, scores candidate fit, and ranks matches through a browser-based UI. Built with Object-Oriented Programming, robust file handling, text processing, and a layered exception hierarchy.

**Version:** 1.0.0  
**License:** MIT

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Architecture & Data Flow](#architecture--data-flow)
6. [Module Reference](#module-reference)
7. [Supported File Formats](#supported-file-formats)
8. [Scoring Algorithm](#scoring-algorithm)
9. [Skill Extraction & Aliases](#skill-extraction--aliases)
10. [Exception Hierarchy](#exception-hierarchy)
11. [Web Interface](#web-interface)
12. [Installation](#installation)
13. [Configuration](#configuration)
14. [Running the Application](#running-the-application)
15. [Production Deployment](#production-deployment)
16. [Usage Guide](#usage-guide)
17. [Development](#development)
18. [Troubleshooting](#troubleshooting)
19. [Limitations & Future Work](#limitations--future-work)
20. [License](#license)

---

## Overview

Smart Resume-to-Job Matcher accepts one or more resume files and a job description, then produces a ranked list of candidates with:

- Overall fit score (0–100)
- Skill coverage score
- Experience score
- Education score
- Matched, missing, and extra skills
- Extracted experience years and required years

The system is designed for HR teams, recruiters, and hiring managers who need a quick, explainable first-pass screening tool.

---

## Key Features

- **Multi-file upload** — analyze many resumes in a single request.
- **Flexible job input** — upload a job description file or paste text directly.
- **Weighted scoring** — skills 50%, experience 30%, education 20% (configurable).
- **Skill aliasing** — recognizes synonyms (e.g., `js` → JavaScript, `k8s` → Kubernetes).
- **Experience & education heuristics** — regex-based extraction with fallbacks.
- **Graceful error handling** — descriptive custom exceptions for missing, empty, or corrupted files.
- **Optional PDF/DOCX support** — lazy imports keep core dependencies minimal.
- **Responsive UI** — clean, mobile-friendly HTML/CSS interface.
- **Temporary file isolation** — uploads are processed in an ephemeral temp directory and never persisted.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| Web Framework | Flask 3.0+ |
| WSGI (production) | Gunicorn (recommended) |
| Frontend | HTML5, CSS3 (no JS framework) |
| File Parsing | Standard library + optional `pypdf`, `python-docx` |
| Data Modeling | `dataclasses` |

---

## Project Structure

```
resume_matcher/            # Core domain package
  __init__.py             # Public API exports
  exceptions.py           # Custom exception hierarchy
  models.py               # Candidate, JobDescription, MatchResult dataclasses
  file_handler.py         # Safe reading, validation, encoding handling
  skills.py               # Skill database, aliases, extraction helpers
  parser.py               # ResumeParser, JobParser
  scorer.py               # Weighted scoring engine
  matcher.py              # Orchestration and ranking
  reporter.py             # Console/text report formatting

templates/
  index.html              # Upload form + results view

static/
  style.css               # Application styling

data/
  resumes/                # Sample resumes
  jobs/                   # Sample job description

app.py                    # Flask entry point
requirements.txt          # Python dependencies
README.md                 # This document
.gitignore
```

---

## Architecture & Data Flow

```
Browser (upload)
   │
   ▼
Flask route /match
   │
   ├─ Save uploaded files to TemporaryDirectory
   │
   ▼
Matcher.match_from_paths()
   │
   ├─ JobParser.parse_file()     ──► JobDescription
   ├─ ResumeParser.parse_file()   ──► Candidate (×N)
   │
   ▼
Scorer.score(candidate, job)     ──► MatchResult (×N)
   │
   ▼
Sort by score (desc) → assign ranks
   │
   ▼
Render templates/index.html with results
```

All file I/O is confined to `file_handler.py`; parsing to `parser.py`; scoring to `scorer.py`. This separation keeps the web layer thin and the domain logic testable.


## Module Reference

### `resume_matcher/__init__.py`
Exports the public API: `Matcher`, `Candidate`, `JobDescription`, `MatchResult`, `Scorer`. Package version `1.0.0`.

### `resume_matcher/exceptions.py`
Base exception `ResumeMatcherError` with subclasses:
- `FileValidationError` — missing/wrong-type/empty file.
- `FileReadError` — file exists but cannot be read/decoded.
- `ParsingError` — reserved for parse failures.
- `EmptyContentError(FileValidationError)` — empty or whitespace-only file.
- `UnsupportedFileTypeError(FileValidationError)` — unsupported extension.

### `resume_matcher/models.py`
Dataclasses:
- `Candidate`: name, source_path, raw_text, skills, experience_years, education, keywords; `to_dict()`.
- `JobDescription`: title, source_path, raw_text, required_skills, preferred_skills, min_experience_years, education_requirements; `to_dict()`.
- `MatchResult`: candidate, job, score, skill_score, experience_score, education_score, matched/missing/extra skills, rank; `to_dict()`.

### `resume_matcher/file_handler.py`
- `SUPPORTED_TEXT_EXTENSIONS` = `{.txt, .md, .markdown, .csv, .log, .rst}`
- `OPTIONAL_EXTENSIONS` = `{.pdf, .docx}`
- `ALL_SUPPORTED` = union
- `ENCODING_CANDIDATES` = `utf-8, utf-8-sig, latin-1, cp1252`
- Functions: `validate_file_path`, `read_file`, `read_files`, `collect_resume_files`, `is_readable`.

PDF/DOCX readers are lazy-imported (`pypdf`, `python-docx`) and raise `FileReadError` with install instructions when missing.

### `resume_matcher/skills.py`
- `SKILL_ALIASES`: canonical skill → alias list (50+ skills).
- `EDUCATION_KEYWORDS`, `EXPERIENCE_PATTERNS`.
- `normalize_text`, `extract_skills`, `extract_experience_years`, `extract_education`, `extract_name`, `extract_keywords`.

Skill matching uses word-boundary regex (`(?<![a-z0-9+#.])alias(?![a-z0-9+#.])`) to avoid false positives.

### `resume_matcher/parser.py`
- `ResumeParser.parse_text` / `parse_file` → `Candidate`.
- `JobParser.parse_text` / `parse_file` → `JobDescription`.
- Job parser splits required vs preferred skills via section headings (`required`, `must have`, `mandatory`, `preferred`, `nice to have`, `optional`, `bonus`).

### `resume_matcher/scorer.py`
- `Scorer(skill_weight=0.5, experience_weight=0.3, education_weight=0.2, preferred_bonus=0.1)`.
- Validates weights sum to 1.0.
- `score(candidate, job)` → `MatchResult`.
- Education score uses token overlap with a 0.6 floor when a degree keyword is present.

### `resume_matcher/matcher.py`
- `Matcher(scorer=None, skill_aliases=None)`.
- `match_candidate`, `match_candidates`, `match_from_paths`, `match_from_directory`, `match_texts`.

### `resume_matcher/reporter.py`
- `format_result_table`, `format_detailed`, `write_report` (retained for programmatic use).

### `app.py`
Flask application:
- `GET /` → render upload form.
- `POST /match` → process uploads, render results.
- `MAX_CONTENT_LENGTH` = 16 MB.
- Secret key from `SECRET_KEY` env var (fallback for dev).

---

## Supported File Formats

| Extension | Type | Notes |
|---|---|---|
| `.txt`, `.md`, `.markdown`, `.csv`, `.log`, `.rst` | Text | Multi-encoding read (utf-8 → utf-8-sig → latin-1 → cp1252) |
| `.pdf` | Binary | Requires `pypdf` |
| `.docx` | Binary | Requires `python-docx` |

Empty or whitespace-only files raise `EmptyContentError`.

---

## Scoring Algorithm

Final score (0–100):

```
score = (skill_score * 0.5 + experience_score * 0.3 + education_score * 0.2) * 100
```

**Skill score (0–1):**
- `skill_core = matched_required / required_skills` (1.0 if no required skills).
- `preferred_ratio = matched_preferred / preferred_skills` (0 if none).
- `skill_score = min(skill_core + preferred_ratio * 0.1, 1.0)`.

**Experience score (0–1):**
- If `min_experience_years > 0`: `min(candidate_years / required_years, 1.0)`.
- Else: `1.0` if candidate has experience, else `0.5`.

**Education score (0–1):**
- If job has education requirements: token-overlap ratio; floor of 0.6 if candidate text contains a degree keyword.
- Else: `1.0` if candidate has education, else `0.5`.

Weights and preferred bonus are configurable via the `Scorer` constructor (must sum to 1.0).

## Skill Extraction & Aliases

Canonical skills are derived from `SKILL_ALIASES` in `resume_matcher/skills.py`. Examples:

| Canonical | Aliases |
|---|---|
| `python` | python, py |
| `javascript` | javascript, js, ecmascript |
| `kubernetes` | kubernetes, k8s |
| `machine learning` | machine learning, ml |
| `rest api` | rest, rest api, restful |
| `git` | git, github, gitlab, version control |

To extend, add entries to `SKILL_ALIASES`. No code changes elsewhere are required.

---

## Exception Hierarchy

```
ResumeMatcherError (base)
├── FileValidationError
│   ├── EmptyContentError
│   └── UnsupportedFileTypeError
├── FileReadError
└── ParsingError
```

The web layer catches `ResumeMatcherError` and surfaces a user-friendly flash message; unexpected exceptions are also caught and reported.

---

## Web Interface

### Routes

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Render upload form |
| `POST` | `/match` | Process uploads and render ranked results |

### Form Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `resumes` | file (multiple) | Yes | Resume files |
| `job_file` | file | No | Job description file |
| `job_text` | textarea | Conditional | Job description text (required if no job file) |

### Results Display

- Ranked table: Rank, Candidate, Score, Skill, Experience, Education.
- Per-candidate cards: matched/missing/extra skills, experience years vs required.

---

## Installation

### Prerequisites

- Python 3.9 or newer
- pip

### Steps

```bash
# Clone
git clone <repository-url>
cd "Resume Matcher"

# Virtual environment (recommended)
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Optional dependencies (PDF/DOCX)

Uncomment in `requirements.txt` or install directly:

```bash
pip install pypdf python-docx
```

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `resume-matcher-secret-key` | Flask session signing key (change in production) |
| `PORT` | `5000` | Server port |

Set via shell:

```bash
# Windows (PowerShell)
$env:SECRET_KEY = "a-strong-random-secret"
$env:PORT = "8080"

# macOS/Linux
export SECRET_KEY="a-strong-random-secret"
export PORT=8080
```

---

## Running the Application

### Development

```bash
python app.py
```

Open http://127.0.0.1:5000.

Debug mode is enabled by default in `app.py` (`debug=True`). Disable for production.

### Production (recommended)

Use a production WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

On Windows, use `waitress`:

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

---

## Production Deployment

### Checklist

- [ ] Set a strong `SECRET_KEY`.
- [ ] Disable debug mode (`debug=False` or remove from `app.run`).
- [ ] Run behind a reverse proxy (Nginx/Caddy) with HTTPS.
- [ ] Set `MAX_CONTENT_LENGTH` appropriately.
- [ ] Use a production WSGI server (Gunicorn/Waitress/uWSGI).
- [ ] Restrict upload size and validate file types (already enforced).
- [ ] Configure logging and monitoring.
- [ ] Run as a non-root user.

### Example Nginx snippet

```nginx
server {
    listen 80;
    server_name example.com;
    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker (optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV SECRET_KEY=change-me
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## Usage Guide

1. Start the app (`python app.py`).
2. Open the browser UI.
3. Select one or more resume files (`.txt`, `.md`, `.pdf`, `.docx`, etc.).
4. Provide a job description either by uploading a file or pasting text.
5. Click **Match Resumes**.
6. Review the ranked table and per-candidate detail cards.

Sample data is provided in `data/resumes/` and `data/jobs/senior_python_backend.txt` for quick testing.

---

## Development

### Code style

- Follow PEP 8.
- Use type hints where practical.
- Keep I/O in `file_handler.py`, parsing in `parser.py`, scoring in `scorer.py`.

### Extending skills

Edit `SKILL_ALIASES` in `resume_matcher/skills.py`. The matcher picks up new aliases automatically.

### Tuning weights

```python
from resume_matcher.scorer import Scorer
scorer = Scorer(skill_weight=0.6, experience_weight=0.25, education_weight=0.15)
```

### Programmatic API

```python
from resume_matcher.matcher import Matcher

matcher = Matcher()
results = matcher.match_from_paths(
    ["data/resumes/jane_doe.txt", "data/resumes/bob_lee.txt"],
    "data/jobs/senior_python_backend.txt",
)
for r in results:
    print(r.rank, r.candidate.name, r.score)
```

Or from in-memory text:

```python
matcher.match_texts(
    resume_texts=[resume1_text, resume2_text],
    job_text=job_text,
    names=["Jane Doe", "Bob Lee"],
)
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: flask` | Dependencies not installed | `pip install -r requirements.txt` |
| `pypdf`/`python-docx` errors | Optional package missing | Install the relevant package |
| "File is empty" flash | Uploaded empty file | Upload a non-empty resume |
| "Unsupported file type" | Extension not in `ALL_SUPPORTED` | Convert to supported format |
| Upload too large | Exceeds 16 MB | Increase `MAX_CONTENT_LENGTH` or reduce file size |
| Port in use | Another process on port | Set `PORT` env var |
| No results rendered | No valid resumes parsed | Check file contents and formats |

---

## Limitations & Future Work

- Skill extraction is dictionary-based; novel skills not in `SKILL_ALIASES` are missed.
- Experience/education extraction is heuristic and may misparse unusual formats.
- No persistence: results are not stored between sessions.
- No authentication/authorization (single-tenant).
- No asynchronous processing for very large batches.
- Potential future additions: CI/CD, type checking (mypy), broader tests, scoring-config file, database persistence, REST API, multi-language support.

---

## License

MIT License. See `LICENSE`

