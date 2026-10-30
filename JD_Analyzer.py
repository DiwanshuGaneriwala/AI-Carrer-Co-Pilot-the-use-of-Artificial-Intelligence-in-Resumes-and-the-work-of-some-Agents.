import re
import spacy
from spacy.matcher import PhraseMatcher


class JobDescriptionAnalyzer:
    DEFAULT_SKILLS = [
        "Python", "java", "c++", "javascript", "typescript", "react", "vue",
        "angular", "fastapi", "django", "flask", "sql", "postgresql", "mysql",
        "sqlite", "mongodb", "redis", "docker", "kubernetes", "aws", "gcp",
        "azure", "git", "linux", "pytorch", "tensorflow", "scikit-learn",
        "spacy", "nlp", "rest api", "graphql", "html", "css", "tailwind"
    ]

    def __init__(self, spacy_model: str = "en_core_web_sm", custom_skills: list = None):
        self.nlp = self._load_spacy_model(spacy_model)
        self.skills_list = list(set(self.DEFAULT_SKILLS + (custom_skills or [])))
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = [self.nlp.make_doc(skill) for skill in self.skills_list]
        self.matcher.add("SKILLS", patterns)

    @staticmethod
    def _load_spacy_model(spacy_model: str):
        try:
            return spacy.load(spacy_model)
        except OSError:
            return spacy.blank("en")

    def extract_required_skills(self, text: str) -> list[str]:
        doc = self.nlp(text)
        matches = self.matcher(doc)
        found_skills = {doc[start:end].text.title() for _, start, end in matches}
        return sorted(found_skills)

    def extract_experience_years(self, text: str) -> int:
        pattern = r"(\d+)\+?\s*(?:to\s*\d+\s*)?(?:years?|yrs?)(?:\s+of)?\s+experience"
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return max(int(m) for m in matches)
        return 0

    def analyze(self, jd_text: str) -> dict:
        return {
            "required_skills": self.extract_required_skills(jd_text),
            "min_experience_years": self.extract_experience_years(jd_text),
            "raw_text_length": len(jd_text),
        }