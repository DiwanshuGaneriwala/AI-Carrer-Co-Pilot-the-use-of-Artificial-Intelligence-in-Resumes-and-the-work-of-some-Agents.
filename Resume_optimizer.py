import json
import os
from typing import Dict, List, Optional
from openai import OpenAI

class ResumeOptimizer:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url=base_url) if api_key else None

    def generate_suggestions(
            self,
            resume_data: Dict,
            target_jd: str,
            missing_skills: List[str]
    ) -> Dict:
        if self.client is None:
            raise RuntimeError("Set the OPENAI_API_KEY environment variable to generate resume improvements.")

        prompt = f"""
You are an expert ATS (Application Tracking System) and executive technical carrer coach.
Analyse the following parsed resume against the provided Job Descritpion and identified skill gaps.

Target Job Description:
{target_jd}

Identified Missing Skills:
{", ".join(missing_skills) if missing_skills else "None"}

Candidate's Current Experience & Projects:
Experince: {json.dumps(resume_data.get('work_experience', []))}
Projects: {json.dumps(resume_data.get('projects', []))}

Return ONLY a valid JSON object matching this schema:
{{
    "ats_score_estimate": <number 0-100>,
    "formatting_fixes": ["formatting or section placement tips"],
    "missing_section_alerts": ["missing section or certification"],
    "bullet_improvements": [
    {{
        "original": "<original bullet text>",
        "improved": "<rewritten bullet using XYZ format: Accomplished [X] as measured by [Y] by doing [Z]>",
        "reason": "<why this improves ATS match and recruiter clarity>"
    }}
    ],
    "keyword_integrated_advice": ["specific recommendations to include relevant skills honestly"]
}}
"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise career coach that responds strictly in JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content)