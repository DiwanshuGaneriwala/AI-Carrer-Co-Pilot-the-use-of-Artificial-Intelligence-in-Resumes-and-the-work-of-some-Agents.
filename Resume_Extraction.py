import re
import spacy
from spacy.matcher import PhraseMatcher

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

COMMON_SKILLS = [
    "Python", "JAVA", "C++", "JavaScript", "TypeScript", "React", "ReactPy",
    "FastAPI", "Flask", "Django", "Pytorch", "TensorFlow", "spaCy", "FAISS",
    "Chroma", "SQL", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "Git",
    "Salesforce", "Apex", "Tailwind CSS", "HTML", "CSS", "NLP", "Machine Learning"
]

class ResumeInfoExtractor:
    def __init__(self, skills_list=None):
        self.skills_list = skills_list if skills_list is not None else COMMON_SKILLS
        self.matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = [nlp.make_doc(skill) for skill in self.skills_list]
        self.matcher.add("SKILLS", patterns)

    def extract_contact_info(self, text: str) -> dict:
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-z0-9-.]+"
        phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        linkedin_pattern = r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+"
        github_pattern = r"(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+"

        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        linkedins = re.findall(linkedin_pattern, text)
        githubs = re.findall(github_pattern, text)

        return {
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "linkedin": linkedins[0] if linkedins else None,
            "github": githubs[0] if githubs else None,
        }

    def extract_name(self, doc) -> str:
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) <= 4:
                return ent.text

        lines = [line.strip() for line in doc.text.split("\n") if line.strip()]
        return lines[0] if lines else "Candidate"

    def extract_skills(self, doc) -> list:
        matches = self.matcher(doc)
        canonical_skills = {skill.casefold(): skill for skill in self.skills_list}
        found_skills = set()
        for match_id, start, end in matches:
            matched_skill = doc[start:end].text.casefold()
            found_skills.add(canonical_skills[matched_skill])
        return sorted(list(found_skills))

    def segment_sections(self, text: str) -> dict:
        section_headers = [
            "EDUCATION", "EXPERIENCE", "WORK EXPERIENCE",
            "PROJECTS", "SKILLS", "CERTIFICATIONS", "PUBLICATIONS"
        ]
        pattern = r"(?i)^(" + "|".join(section_headers) + r")\s*$"
        lines = text.split("\n")
        sections = {}
        current_section = "GENERAL"
        sections[current_section] = []

        for line in lines:
            stripped = line.strip()
            if re.match(pattern, stripped):
                current_section = stripped.upper()
                sections[current_section] = []
            else:
                sections[current_section].append(line)

        return {k: "\n".join(v).strip() for k, v in sections.items() if v}

    def extract(self, raw_text: str) -> dict:
        doc = nlp(raw_text)
        contact = self.extract_contact_info(raw_text)
        name = self.extract_name(doc)
        skills = self.extract_skills(doc)
        sections = self.segment_sections(raw_text)

        return {
            "name": name,
            "contact": contact,
            "skills": skills,
            "sections": sections,
        }