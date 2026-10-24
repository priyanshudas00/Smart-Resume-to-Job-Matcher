# Smart Resume-to-Job Matcher

A Python web application that parses resumes and job descriptions, scores candidate fit, and ranks matches through a browser UI. Built with Object-Oriented Programming, file handling, string operations, and exception handling.

## Features

- Upload multiple resumes and a job description (file or pasted text) via a browser UI.
- Weighted scoring: skills 50%, experience 30%, education 20%.
- Skill extraction via alias dictionary with word-boundary regex.
- Experience and education heuristics.
- Optional PDF/DOCX support via lazy imports (`pypdf`, `python-docx`).
- Custom exception hierarchy for validation/read/parse errors.
- Responsive HTML/CSS interface.

## Project Structure

```
resume_matcher/   # core package
  exceptions.py    # custom exceptions
  models.py        # Candidate, JobDescription, MatchResult
  file_handler.py  # safe file reading & validation
  skills.py        # skill database & extraction
  parser.py        # resume/job parsers
  scorer.py        # scoring engine
  matcher.py       # orchestration & ranking
  reporter.py      # output formatting
templates/         # HTML templates
static/            # CSS
data/              # sample resumes and job descriptions
app.py             # Flask entry point
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

## Run

```bash
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

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

