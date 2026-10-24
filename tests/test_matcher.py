import os
import tempfile
import unittest

from resume_matcher.matcher import Matcher


class TestMatcher(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.resumes = os.path.join(self.tmp, "resumes")
        self.jobs = os.path.join(self.tmp, "jobs")
        os.makedirs(self.resumes)
        os.makedirs(self.jobs)
        with open(os.path.join(self.resumes, "r1.txt"), "w") as f:
            f.write("Alice\nSkills: Python, SQL, Docker\nExperience: 6 years of experience\nEducation: Bachelor")
        with open(os.path.join(self.resumes, "r2.txt"), "w") as f:
            f.write("Bob\nSkills: Java\nExperience: 1 year of experience\nEducation: Associate")
        with open(os.path.join(self.jobs, "job.txt"), "w") as f:
            f.write("Job Title: Backend\nRequired: Python, SQL, Docker\nExperience: 5 years\nEducation: Bachelor")

    def test_match_from_directory(self):
        m = Matcher()
        results = m.match_from_directory(self.resumes, os.path.join(self.jobs, "job.txt"))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].candidate.name, "Alice")
        self.assertEqual(results[0].rank, 1)
        self.assertGreater(results[0].score, results[1].score)

    def test_match_texts(self):
        m = Matcher()
        results = m.match_texts(
            ["Skills: Python, SQL\nExperience: 5 years\nEducation: Bachelor"],
            "Required: Python, SQL\nExperience: 3 years\nEducation: Bachelor",
            names=["X"],
        )
        self.assertEqual(results[0].candidate.name, "X")
        self.assertGreaterEqual(results[0].score, 0)


if __name__ == "__main__":
    unittest.main()
