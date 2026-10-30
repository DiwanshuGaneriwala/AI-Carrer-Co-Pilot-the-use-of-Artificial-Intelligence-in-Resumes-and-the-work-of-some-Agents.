import re
import spacy
from spacy.matcher import PhraseMatcher


class ResumeInfoExtractor:
    SECTION_HEADERS = {
        "education": [
            "education", "academic background", "qualifications",
            "academic details", "degrees"
        ],
        "work_experience": [
            "work experience", "professional experience", "employment history",
            "experience", "internships", "work history"
        ],
        "projects": [
            "projects", "project experience", "key projects"
        ],
        "certifications": [
            "certifications", "licenses", "certifications and licenses",
            "courses & certificates", "credentials"
        ],
        "skills": [
            "skills", "technical skills", "core competencies",
            "technologies", "tool & technologies", "skills & tools"
        ]
    }

    DEFAULT_SKILLS = [
        "python", "java", "c++", "javascript", "typescript", "react", "vue",
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

    def __extract_name(self, text: str) -> str:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return ""

        header_text = "\n".join(lines[:5])
        doc = self.nlp(header_text)

        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                if not any(token in ent.text.lower() for token in ["resume", "curriculum", "page"]):
                    return ent.text.strip()

        for line in lines[:3]:
            if not re.search(r"(@|phone|https?:|linkedin|github)", line, re.I):
                if len(line.split()) in [2, 3, 4]:
                    return line

        return ""

    def _segment_sections(self, text: str) -> dict:
        sections = {sec: "" for sec in self.SECTION_HEADERS.keys()}
        current_section = None
        current_lines = []

        def flush_section():
            nonlocal current_section, current_lines
            if current_section is not None:
                sections[current_section] += ("\n" + "\n".join(current_lines)).strip() + "\n"
                current_section = None
                current_lines = []

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                if current_section is not None:
                    current_lines.append("")
                continue

            matched_section = None
            normalized_line = re.sub(r"\s+", " ", line).lower()

            for section_name, headers in self.SECTION_HEADERS.items():
                for header in headers:
                    if normalized_line == header.lower() or normalized_line.startswith(header.lower() + ":"):
                        matched_section = section_name
                        break
                if matched_section:
                    break

            if matched_section:
                flush_section()
                current_section = matched_section
                continue

            if current_section is not None:
                current_lines.append(raw_line)

        flush_section()
        return {k: v.strip() for k, v in sections.items()}

    def _extract_skills(self, text: str, skills_section_text: str = "") -> list:
        target_text = skills_section_text if skills_section_text else text
        doc = self.nlp(target_text)
        matches = self.matcher(doc)

        found_skills = set()
        for _, start, end in matches:
            found_skills.add(doc[start:end].text.title())

        return sorted(found_skills)

    def _clean_blocks_items(self, block_text: str) -> list:
        if not block_text:
            return []
        raw_items = re.split(r"(?:\n\s*[-.*]\s*|\n{2,})", block_text)
        return [item.strip() for item in raw_items if len(item.strip()) > 5]

    def extract(self, text: str) -> dict:
        sections = self._segment_sections(text)
        name = self.__extract_name(text)
        skills = self._extract_skills(text, sections.get("skills", ""))
        education = self._clean_blocks_items(sections.get("education", ""))
        experience = self._clean_blocks_items(sections.get("work_experience", ""))
        projects = self._clean_blocks_items(sections.get("projects", ""))
        certifications = self._clean_blocks_items(sections.get("certifications", ""))

        return {
            "name": name,
            "skills": skills,
            "education": education,
            "work_experience": experience,
            "projects": projects,
            "certifications": certifications,
        }