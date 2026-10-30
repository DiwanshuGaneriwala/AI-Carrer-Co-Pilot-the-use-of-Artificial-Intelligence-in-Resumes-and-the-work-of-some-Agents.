import sqlite3
from typing import Dict

class AnalyticsDashboardTracker:
    def __init__(self, db_path: str = "storage/carrer_analytics.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS score_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id TEXT,
                    target_role TEXT,
                    semantic_score REAL,
                    skill_coverage_pct REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interview_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id TEXT,
                    question TEXT,
                    score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def record_match_snapshot(self, resume_id: str, target_role: str, semantic_score: float, coverage_pct: float):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO score_history (resume_id, target_role, semantic_score, skill_coverage_pct) VALUES (?, ?, ?, ?)",
                (resume_id, target_role, semantic_score, coverage_pct)
            )
            conn.commit()

    def record_interview_score(self, resume_id: str, question: str, score: float):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO interview_history (resume_id, question, score) Values (?, ?, ?)",
                (resume_id, question, score)
            )
            conn.commit()

    def get_progress_summary(self, resume_id: str) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT semantic_score, skill_coverage_pct, timestamp FROM score_history WHERE resume_id = ? ORDER BY timestamp ASC",
                (resume_id,)
            )
            match_rows = cursor.fetchall()

            cursor.execute(
                "SELECT score, timestamp FROM interview_history WHERE resume_id = ? ORDER BY timestamp ASC",
                (resume_id,)
            )            
            interview_rows = cursor.fetchall()

            return {
                "score_progression": [
                    {"score": r[0], "coverage": r[1], "date": r[2]} for r in match_rows
                ],
                "interview_progression": [
                    {"score": r[0], "date": r[1]} for r in interview_rows
                ],
                "total_iterations": len(match_rows),
                "latest_match_score": match_rows[-1][0] if match_rows else 0.0,
                "average_interview_score": round(sum(r[0] for r in interview_rows) / len(interview_rows), 2) if interview_rows else 0.0
            }