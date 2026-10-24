"""Flask web application for the Smart Resume-to-Job Matcher."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from resume_matcher.exceptions import ResumeMatcherError
from resume_matcher.file_handler import ALL_SUPPORTED
from resume_matcher.matcher import Matcher

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "resume-matcher-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", results=None)


@app.route("/match", methods=["POST"])
def match():
    resume_files = request.files.getlist("resumes")
    job_file = request.files.get("job_file")
    job_text = (request.form.get("job_text") or "").strip()

    if not resume_files or all(f.filename == "" for f in resume_files):
        flash("Please upload at least one resume file.", "error")
        return redirect(url_for("index"))

    if job_file is None or job_file.filename == "":
        if not job_text:
            flash("Please upload a job description file or paste job text.", "error")
            return redirect(url_for("index"))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        resume_paths: list[str] = []
        try:
            for f in resume_files:
                if f.filename == "":
                    continue
                safe_name = secure_filename(f.filename)
                if not safe_name:
                    continue
                dest = tmp / safe_name
                f.save(dest)
                resume_paths.append(str(dest))

            if job_file is not None and job_file.filename != "":
                safe_job = secure_filename(job_file.filename)
                job_path = tmp / safe_job
                job_file.save(job_path)
            else:
                job_path = tmp / "job_description.txt"
                job_path.write_text(job_text, encoding="utf-8")

            if not resume_paths:
                flash("No valid resume files were uploaded.", "error")
                return redirect(url_for("index"))

            matcher = Matcher()
            results = matcher.match_from_paths(resume_paths, str(job_path))
        except ResumeMatcherError as exc:
            flash(f"Processing error: {exc}", "error")
            return redirect(url_for("index"))
        except Exception as exc:  # noqa: BLE001
            flash(f"Unexpected error: {exc}", "error")
            return redirect(url_for("index"))

    results_data = [r.to_dict() for r in results]
    # attach candidate name already in dict; keep full result objects for template
    return render_template("index.html", results=results, results_data=results_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
