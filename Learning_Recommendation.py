from typing import Dict, List
from urllib.parse import quote

class LearningRecommender:
    KNOWLEDGE_BASE: Dict[str, Dict] = {
        "Docker": {
            "topic": "Containerization & Orchestration Fundamentals",
            "difficulty": "Beginner to Intermediate",
            "documentation": "https://docs.docker.com/get-started/",
            "recommended_project": "Containerize a FastAPI app with multi-stage builds and PostgreSQL database.",
            "estimated_hours": 12
        },
        "Kubernetes": {
            "topic": "Production Cluster Deployment & Helm Charts",
            "difficulty": "Intermediate to Advanced",
            "documentation": "https://kubernetes.io/docs/tutorials/",
            "recommended_project": "Deploy a microservice cluster using Minikube, ingress controllers, and ConfigMaps.",
            "estimated_hours": 25
        },
        "Fastapi": {
            "topic": "High-Performance Asynchronous Python APIs",
            "difficulty": "Beginner to Intermediate",
            "documentation": "https://fastapi.tiangolo.com/tutorial/",
            "recommended_project": "Build an asynchronous CRUD service with Pydantic validation and JWT authentication.",
            "estimated_hours": 10
        },
        "Aws": {
            "topic": "Cloud Infrastructure, IAM, S3, & Serverless Lambda",
            "difficulty": "Intermediate",
            "documentation": "https://aws.amazon.com/getting-started/",
            "recommended_project": "Set up an S3-triggered AWS Lambda function integrated with API Gateway.",
            "estimated_hours": 20
        },
        "Postgresql": {
            "topic": "Relational Schema Design, Indexing & Query Tuning",
            "difficulty": "Beginner to Intermediate",
            "documentation": "https://www.postgresql.org/docs/",
            "recommended_project": "Design a relational schema with EXPLAIN ANALYZE index optimization and connection pooling.",
            "estimated_hours": 15
        }
    }

    def recommend(self, missing_skills: List[str]) -> List[Dict]:
        recommendations = []
        for skill in missing_skills:
            canonical = skill.strip().title()
            if canonical in self.KNOWLEDGE_BASE:
                item = self.KNOWLEDGE_BASE[canonical].copy()
                item["skill"] = canonical
                recommendations.append(item)
            else:
                recommendations.append({
                    "skill": canonical,
                    "topic": f"Mastery of {canonical} for Production Environments",
                    "difficulty": "General",
                    "documentation": f"https://www.google.com/search?q={quote(canonical)}+official+documentation",
                    "recommended_project": f"Create an open-source GitHub repository demonstrating {canonical} core concepts.",
                    "estimated_hours": 15
                })
        return recommendations