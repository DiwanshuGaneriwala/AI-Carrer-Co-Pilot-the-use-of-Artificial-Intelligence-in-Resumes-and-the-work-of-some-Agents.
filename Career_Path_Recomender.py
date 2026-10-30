from typing import Dict, List
from sentence_transformers import SentenceTransformer, util

class CareerPathRecomender:
    ROLE_TAXONOMY: Dict[str, str] = {
        "Data Analyst": "SQL, Excel Tableau, Power BI, Python, Pandas, Data Visualization, Statistics",
        "BI Analyst": "Business Intelligence, Power BI, Tableau, ETL Pipelines, SQL, Data Warehousing, KPI Dashboards",
        "Meachine Learning Engineer": "Python, Pytorch, TensorFlow, Sckit-Learn, MLOps, Docker, REST API, Model Deployment",
        "Backend Engineer": "Python, FastAPI, Django, PostgreSQL, Redis, Docker, REST API, Microsevices, System Design",
        "Full Stack Developer": "JavaScript, TypesScript, React, Node.js, HTML, CSS, Tailwind, PostgreSQL, REST API",
        "Cloud & DevOps Engineer": "Docker, Kubernetes, AWS, Terraform, CI/CD, Linux, Bash, Git, Monitoring, Networking"
    }

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.role_names = list(self.ROLE_TAXONOMY.keys())
        role_texts = [f"{role}: {skills}" for role, skills in self.ROLE_TAXONOMY.items()]
        self.role_embeddings = self.model.encode(role_texts, convert_to_tensor=True)

    def recommend_paths(self, candidate_skills: List[str], current_target_role: str = "") -> List[Dict]:
        candidate_text = ", ".join(candidate_skills)
        candidate_embedding = self.model.encode(candidate_text, convert_to_tensor=True)

        similarities = util.cos_sim(candidate_embedding, self.role_embeddings)[0]
        results = []

        for idx, score in enumerate(similarities):
            role_name = self.role_names[idx]
            if role_name.lower() == current_target_role.lower():
                continue

            match_pct = round(max(0.0, float(score.item())) * 100, 2)
            results.append({
                "role": role_name,
                "match_percentage": match_pct,
                "key_associated_skills": self.ROLE_TAXONOMY[role_name]
            })

        return sorted(results, key=lambda x : x["match_percentage"], reverse=True)