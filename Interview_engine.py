import json
import os
from typing import Dict, List, Optional
from openai import OpenAI

class InterviewEngine:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url=base_url) if api_key else None

    def _require_client(self):
        if self.client is None:
            raise RuntimeError("Set the OPENAI_API_KEY environment variable to use interview questions and scoring.")
        return self.client

    def generate_interview_questions(self, target_role: str, jd_text: str, candidate_skills: List[str]) -> List[Dict]:
        """Module 8: Generates role-specific questions"""
        prompt = f"""
    You are a senior technical hiring manager interviewing a candidate for the role of: {target_role}.
Job_Description context:
{jd_text[:1000]}

Candidate Skills: {", ".join(candidate_skills)}

Generate 5 high-quality interview questions (3 Technical, 2 Behavioural/System Scenario).
Return Strictly a Json object matching this schema:
{{
    "questions": [
        {{
            "id": 1,
            "category": "Technical | Behavioural | Scenario",
            "question": "<The question text>",
            "target_competency": "<competency evaluated>" 
        }}
    ]
}}
"""
        response = self._require_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.4
        )
        return json.loads(response.choices[0].message.content).get("questions", [])

    def score_answere(self, question: str, user_answere: str, target_role: str) -> Dict:
        """Module 9: Evaluates user answere with actionalbe scoring and exampler response."""
        prompt = f"""
You are an interview assesor evaluating a candidate's answere for a {target_role} position.

Question: {question}
Candidates Answer: {user_answere}

Evaluates the response objectively. Return strictly a JSON object:
{{
    "score": <integer 0-100>,
    "criteria_breakdown": {{
        "technical_depth": <0-10>,
        "comunication_depth": <0-10>,
        "relevance": <0-10>
    }},
    "strengths": [<list of strong points>],
    "areas_for_improvement": [<list of missing technical details of fluff>],
    "example_model_answer": "<A top-tier response demonstrating depth and concise impact>"
}}
"""
        response = self._require_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return json.loads(response.choices[0].message.content)