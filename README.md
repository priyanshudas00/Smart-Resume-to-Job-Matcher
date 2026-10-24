# Smart Resume-to-Job Matcher

A Python tool that reads and parses resume and job description files, scores candidate fit, and ranks the best matches. Built with Object-Oriented Programming, file handling, string operations, and exception handling.

## Features

- Parse resumes and job descriptions from `.txt`, `.md`, `.csv`, `.pdf` (optional), and `.docx` (optional) files.
- Extract skills, years of experience, education, and keywords using text processing.
- Score candidates on skills, experience, and education with configurable weights.
- Rank candidates and produce console, text, and JSON reports.
- Graceful handling of missing, empty, or corrupted files.
- Command-line interface for matching and file validation.

## Project Structure

```
resume_matcher/        # package
  exceptions.py       # custom exceptions
  models.py           # Candidate, JobDescription, MatchResult
  file_handler.py     # safe file reading & validation
  skills.py           # skill database & extraction
  parser.py           # resume/job parsers
  scorer.py           # scoring engine
  matcher.py          # orchestration & ranking
  reporter.py         # output formatting
  cli.py              # command-line interface
data/                 # sample resumes and job descriptions
tests/                # unit tests
main.py               # script entry point
```

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Optional (for PDF/DOCX support):

```bash
pip install pypdf python-docx
```

## Usage

### Match resumes in a directory against a job description

```bash
python main.py match --resumes data/resumes --job data/jobs/senior_python_backend.txt
```

### Match specific files

```bash
python main.py match -r data/resumes/jane_doe.txt data/resumes/alice_johnson.txt -j data/jobs/senior_python_backend.txt -o report.txt --json results.json
```

### Validate input files

```bash
python main.py validate data/resumes/*.txt
```

### Run as a module

```bash
python -m resume_matcher match --resumes data/resumes --job data/jobs/senior_python_backend.txt
```

## Running Tests

```bash
pytest -q
```

## Scoring

Final score (0-100) is a weighted combination:

- **Skills (50%)**: required skill coverage + preferred skill bonus
- **Experience (30%)**: candidate years / required years (capped at 100%)
- **Education (20%)**: keyword overlap between candidate and job education requirements

Weights are configurable via the `Scorer` class.

## Exception Handling

All file operations are wrapped to raise descriptive custom exceptions:
`FileValidationError`, `FileReadError`, `EmptyContentError`, `UnsupportedFileTypeError`.

## License

MIT
