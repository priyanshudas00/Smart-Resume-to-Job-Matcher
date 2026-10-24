import unittest

from resume_matcher.models import Candidate, JobDescription
from resume_matcher.scorer import Scorer


class TestScorer(unittest.TestCase):
    def setUp(self):
        self.job = JobDescription(
            title="Backend",
            source_path="",
            raw_text="",
            required_skills=["python", "sql", "docker"],
            preferred_skills=["aws"],
            min_experience_years=5.0,
            education_requirements=["bachelor"],
        )

    def test_perfect_candidate(self):
        cand = Candidate(
            name="A",
            source_path="",
            raw_text="",
            skills=["python", "sql", "docker", "aws"],
            experience_years=6.0,
            education=["bachelor of science"],
        )
        res = Scorer().score(cand, self.job)
        self.assertGreaterEqual(res.score, 90)

    def test_missing_skills_lower_score(self):
        cand = Candidate(
            name="B",
            source_path="",
            raw_text="",
            skills=["python"],
            experience_years=2.0,
            education=[],
        )
        res = Scorer().score(cand, self.job)
        self.assertLess(res.score, 60)
        self.assertIn("sql", res.missing_skills)

    def test_weights_validation(self):
        with self.assertRaises(ValueError):
            Scorer(skill_weight=0.5, experience_weight=0.5, education_weight=0.5)

    def test_ranking(self):
        pass


if __name__ == "__main__":
    unittest.main()
