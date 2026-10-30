from difflib import SequenceMatcher

class ResumeMatcher:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.util = None
        self._model_attempted = False

    def _load_model(self):
        if self._model_attempted:
            return

        self._model_attempted = True
        try:
            from sentence_transformers import SentenceTransformer, util

            self.model = SentenceTransformer(self.model_name)
            self.util = util
        except Exception:
            self.model = None

    def _fallback_similarity(self, resume_text: str, jd_text: str) -> float:
        if not resume_text or not jd_text:
            return 0.0
        score = SequenceMatcher(None, resume_text.lower(), jd_text.lower()).ratio()
        return round(score * 100, 2)

    def compute_similarity(self, resume_text: str, jd_text: str) -> float:
        self._load_model()
        if self.model is not None and self.util is not None:
            try:
                embeddings_resume = self.model.encode(resume_text, convert_to_tensor=True)
                embeddings_jd = self.model.encode(jd_text, convert_to_tensor=True)
                score = self.util.cos_sim(embeddings_resume, embeddings_jd).item()
                return round(max(0.0, score) * 100, 2)
            except Exception:
                pass
        return self._fallback_similarity(resume_text, jd_text)

    def analyze_skill_gap(self, candidate_skills: list[str], required_skills: list[str]) -> dict:
        candidate_set = {str(s).lower() for s in candidate_skills or []}
        matched = []
        missing = []

        for req in required_skills or []:
            normalized_req = str(req).lower()
            if normalized_req in candidate_set:
                matched.append(req)
            else:
                missing.append(req)

        coverage = 100.0 if not required_skills else round((len(matched) / len(required_skills) * 100), 2)
        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "coverage_percentage": coverage,
        }
    