import unittest

from resume_matcher.parser import JobParser, ResumeParser


class TestParser(unittest.TestCase):
    def test_resume_parse_skills(self):
        text = "John Doe\nSkills: Python, SQL, Docker\nExperience: 3 years of experience\nEducation: Bachelor of Science"
        rp = ResumeParser()
        c = rp.parse_text(text)
        self.assertIn("python", c.skills)
        self.assertIn("sql", c.skills)
        self.assertIn("docker", c.skills)
        self.assertEqual(c.experience_years, 3.0)
        self.assertIn("bachelor", c.education)

    def test_job_parse_required_preferred(self):
        text = """Job Title: Backend Engineer
Required: Python, SQL, Docker
Preferred: AWS, Kubernetes
Experience: 5 years of experience
Education: Bachelor's degree
"""
        jp = JobParser()
        job = jp.parse_text(text)
        self.assertIn("python", job.required_skills)
        self.assertIn("aws", job.preferred_skills)
        self.assertEqual(job.min_experience_years, 5.0)

    def test_empty_resume_raises(self):
        rp = ResumeParser()
        with self.assertRaises(ValueError):
            rp.parse_text("   ")

    def test_extract_name(self):
        text = "Alice Johnson\nSkills: Python"
        c = ResumeParser().parse_text(text)
        self.assertEqual(c.name, "Alice Johnson")


if __name__ == "__main__":
    unittest.main()
