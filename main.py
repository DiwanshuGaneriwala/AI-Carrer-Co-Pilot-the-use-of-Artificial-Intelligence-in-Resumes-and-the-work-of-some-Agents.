import os
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from Skill_Gap_Analyzer import SkillGapAnalyzer
from JD_Analyzer import JobDescriptionAnalyzer
from Resume_Extractor import ResumeInfoExtractor
from Resume_matcher import ResumeMatcher
from Resume_Upload import MultiFormatDocumentParser
from Resume_optimizer import ResumeOptimizer
from Learning_Recommendation import LearningRecommender
from Interview_engine import InterviewEngine
from CAREER_RAG import CareerRAGAssistant
from Career_Path_Recomender import CareerPathRecomender
from Analytics_Dashboard import AnalyticsDashboardTracker

os.makedirs("storage/resumes", exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = MultiFormatDocumentParser(options={"reject_empty": True, "enable_ocr": True})
extractor = ResumeInfoExtractor()
jd_analyzer = JobDescriptionAnalyzer()
resume_matcher = ResumeMatcher()
gap_analyzer = SkillGapAnalyzer()
optimizer = ResumeOptimizer()
learning_recommender = LearningRecommender()
interview_engine = InterviewEngine()
rag_assistant = None
path_recommeder = None
analytics_tracker = AnalyticsDashboardTracker()


def get_rag_assistant():
    global rag_assistant
    if rag_assistant is None:
        rag_assistant = CareerRAGAssistant()
    return rag_assistant


def get_path_recommender():
    global path_recommeder
    if path_recommeder is None:
        path_recommeder = CareerPathRecomender()
    return path_recommeder

class JDMatchRequest(BaseModel):
    resume_id: str
    jd_text: str
    target_role: str = ""


class InterviewScoreRequest(BaseModel):
    resume_id: str
    question: str
    answer: str
    target_role: str


class InterviewQuestionsRequest(BaseModel):
    target_role: str
    jd_text: str
    candidate_skills: List[str]


@app.post("/api/match")
async def match_resume_with_jd(payload: JDMatchRequest):
    resume_dir = "storage/resumes"
    matched_files = [
        f for f in os.listdir(resume_dir) if f.startswith(payload.resume_id)
    ]
    if not matched_files:
        raise HTTPException(404, detail="Resume not found")

    file_path = os.path.join(resume_dir, matched_files[0])
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    parsed_resume = parser.parse(file_bytes, matched_files[0])
    resume_data = extractor.extract(parsed_resume["text"])
    jd_data = jd_analyzer.analyze(payload.jd_text)
    semantic_score = resume_matcher.compute_similarity(parsed_resume["text"], payload.jd_text)
    skill_gap = resume_matcher.analyze_skill_gap(resume_data["skills"], jd_data["required_skills"])
    analytics_tracker.record_match_snapshot(
        payload.resume_id,
        payload.target_role,
        semantic_score,
        skill_gap["coverage_percentage"],
    )

    return {
        "semantic_match_percentage": semantic_score,
        "skill_coverage_percentage": skill_gap["coverage_percentage"],
        "matched_skills": skill_gap["matched_skills"],
        "missing_skills": skill_gap["missing_skills"],
        "jd_requirements": jd_data,
    }


MAX_FILE_SIZE_MB = 5


@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, detail="File too large")

    try:
        parsed_doc = parser.parse(contents, file.filename)
    except ValueError as e:
        raise HTTPException(422, detail=str(e))

    structured_data = extractor.extract(parsed_doc["text"])

    resume_id = str(uuid.uuid4())
    save_path = f"storage/resumes/{resume_id}{parsed_doc['extension']}"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(contents)

    return {
        "resume_id": resume_id,
        "filename": parsed_doc["filename"],
        "metadata": parsed_doc["metadata"],
        "structured_data": structured_data,
    }

class SkillGapRequest(BaseModel):
    resume_skills: List[str]
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = []

@app.post("/api/skill/gap-analysis")
async def perform_skill_gap_analysis(payload: SkillGapRequest):
    analysis = gap_analyzer.analyze(
        candidate_skills=payload.resume_skills,
        required_skills=payload.required_skills,
        preferred_skills=payload.preferred_skills,
    )
    return analysis

@app.post("/api/resume/improve")
def get_resume_improvements(payload: dict):
    try:
        return optimizer.generate_suggestions(
            payload["resume_data"], payload["jd_text"], payload.get("missing_skills", [])
        )
    except RuntimeError as e:
        raise HTTPException(503, detail=str(e)) from e

@app.post("/api/learning/recommend")
def get_learning_recommendations(payload: dict):
    return learning_recommender.recommend(payload.get("missing_skills", []))

@app.post("/api/interview/score")
def score_mock_answer(payload: InterviewScoreRequest):
    try:
        result = interview_engine.score_answere(payload.question, payload.answer, payload.target_role)
    except RuntimeError as e:
        raise HTTPException(503, detail=str(e)) from e
    analytics_tracker.record_interview_score(payload.resume_id, payload.question, result["score"])
    return result


@app.post("/api/interview/questions")
def generate_interview_questions(payload: InterviewQuestionsRequest):
    try:
        questions = interview_engine.generate_interview_questions(
            payload.target_role, payload.jd_text, payload.candidate_skills
        )
    except RuntimeError as e:
        raise HTTPException(503, detail=str(e)) from e
    if not questions:
        raise HTTPException(502, detail="The interview question generator returned no questions.")
    return {"questions": questions}


@app.post("/api/rag/chat")
def ask_career_assistant(payload: dict):
    try:
        return {"reply": get_rag_assistant().query(payload["question"])}
    except RuntimeError as e:
        raise HTTPException(503, detail=str(e)) from e

@app.post("/api/career/paths")
def get_adjacent_roles(payload: dict):
    return get_path_recommender().recommend_paths(
        payload["candidate_skills"], payload.get("current_target_role", "")
    )

@app.get("/api/analytics/{resume_id}")
def get_analytics(resume_id: str):
    return analytics_tracker.get_progress_summary(resume_id)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)