import React, { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function CareerDashboard() {
    const [currentStep, setCurrentStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    const [resumeFile, setResumeFile] = useState(null);
    const [resumeId, setResumeId] = useState("");
    const [resumeData, setResumeData] = useState(null);
    const [resumeText, setResumeText] = useState("");

    const [targetRole, setTargetRole] = useState("Software Engineer");
    const [jdText, setJDText] = useState("");

    const [matchResult, setMatchResult] = useState(null);
    const [gapResult, setGapResult] = useState(null);
    const [improvements, setImprovements] = useState(null);
    const [improvementError, setImprovementError] = useState("");
    const [recommendations, setRecommendations] = useState([]);

    const [interviewQuestions, setInterviewQuestions] = useState([{
        id: 0,
        category: "Scenario",
        question: "Describe a challenging project and how you solved a bottleneck.",
        target_competency: "Problem solving",
    }]);
    const [selectedQuestionIndex, setSelectedQuestionIndex] = useState(0);
    const [userAnswer, setUserAnswer] = useState("");
    const [interviewFeedback, setInterviewFeedback] = useState(null);

    const [careerPaths, setCareerPaths] = useState([]);
    const [analytics, setAnalytics] = useState(null);

    const handleUploadResume = async (e) => {
        e.preventDefault();
        if (!resumeFile) return;

        setLoading(true);
        setErrorMessage("");

        try {
            const formData = new FormData();
            formData.append("file", resumeFile);

            const res = await fetch(`${API_BASE}/api/resume/upload`, {
                method: "POST",
                body: formData,
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || "Resume upload failed");
            }

            const data = await res.json();
            setResumeId(data.resume_id);
            setResumeData(data.structured_data);
            setResumeText(data.structured_data?.text || "");

            setCurrentStep(2);
        } catch (err) {
            setErrorMessage(err.message || "Unknown upload error");
        } finally {
            setLoading(false);
        }
    };

    const handleAnalyzeJD = async () => {
        if (!jdText.trim()) return;

        setLoading(true);
        setErrorMessage("");

        try {
            const matchRes = await fetch(`${API_BASE}/api/match`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ resume_id: resumeId, jd_text: jdText, target_role: targetRole }),
            });

            if (!matchRes.ok) throw new Error("JD matching failed");

            const matchJson = await matchRes.json();
            setMatchResult(matchJson);

            const requiredSkills =
                matchJson?.jd_requirements?.required_skills ||
                matchJson?.missing_skills ||
                [];

            const gapRes = await fetch(`${API_BASE}/api/skill/gap-analysis`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    resume_skills: resumeData?.skills || [],
                    required_skills: requiredSkills,
                    preferred_skills: [],
                }),
            });

            if (!gapRes.ok) throw new Error("Skill gap analysis failed");

            const gapJson = await gapRes.json();
            setGapResult(gapJson);
            setCurrentStep(3);
        } catch (err) {
            setErrorMessage(err.message || "Analysis failed");
        } finally {
            setLoading(false);
        }
    };

    const handleFetchImprovementsAndRoadmaps = async () => {
        setLoading(true);
        setErrorMessage("");
        setImprovementError("");

        const missing = gapResult?.required?.missing || matchResult?.missing_skills || [];

        const improvementRequest = fetch(`${API_BASE}/api/resume/improve`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                resume_data: resumeData,
                jd_text: jdText,
                missing_skills: missing,
            }),
        }).then(async (response) => {
            const result = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(result.detail || "Resume improvement generation failed");
            }
            return result;
        });

        const recommendationRequest = fetch(`${API_BASE}/api/learning/recommend`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ missing_skills: missing }),
            }).then(async (response) => {
                const result = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(result.detail || "Learning roadmap generation failed");
                }
                return result?.recommendations || result || [];
            });

        const [improvementResult, recommendationResult] = await Promise.allSettled([
            improvementRequest,
            recommendationRequest,
        ]);

        if (improvementResult.status === "fulfilled") {
            setImprovements(improvementResult.value);
        } else {
            const message = improvementResult.reason?.message || "Resume improvements could not be generated.";
            setImprovementError(message);
        }

        if (recommendationResult.status === "fulfilled") {
            setRecommendations(recommendationResult.value);
        } else if (improvementResult.status === "fulfilled") {
            const message = recommendationResult.reason?.message || "Learning roadmaps could not be generated.";
            setErrorMessage(message);
        }

        setCurrentStep(4);
        setLoading(false);
    };

    const handleStartInterview = () => {
        setCurrentStep(5);
    };

    const handleSubmitInterview = async () => {
        if (!userAnswer.trim()) return;

        setLoading(true);
        setErrorMessage("");

        try {
            const scoreRes = await fetch(`${API_BASE}/api/interview/score`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    resume_id: resumeId,
                    question: interviewQuestion,
                    answer: userAnswer,
                    target_role: targetRole,
                }),
            });

            if (!scoreRes.ok) throw new Error("Interview scoring failed");

            const scoreJson = await scoreRes.json();
            setInterviewFeedback(scoreJson);

            const pathRes = await fetch(`${API_BASE}/api/career/paths`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    candidate_skills: resumeData?.skills || [],
                    current_target_role: targetRole,
                }),
            });

            if (pathRes.ok) {
                const pathJson = await pathRes.json();
                setCareerPaths(pathJson);
            }

            const analyticsRes = await fetch(`${API_BASE}/api/analytics/${resumeId}`);
            if (analyticsRes.ok) {
                const analyticsJson = await analyticsRes.json();
                setAnalytics(analyticsJson);
            }

            setCurrentStep(6);
        } catch (err) {
            setErrorMessage(err.message || "Interview submission failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <h1 style={{ margin: 0, fontSize: "22px", color: "#0F172A" }}>
                    AI Career Co-Pilot Dashboard
                </h1>
                <span style={styles.badge}>Live Connected: localhost:8000</span>
            </header>

            <div style={styles.stepperContainer}>
                {[
                    "1. Upload",
                    "2. Target JD",
                    "3. Match & Gaps",
                    "4. AI Fixes",
                    "5. Interview",
                    "6. Growth & Paths",
                ].map((stepName, idx) => {
                    const stepNum = idx + 1;
                    const isActive = currentStep === stepNum;
                    const isDone = currentStep > stepNum;

                    return (
                        <div
                            key={stepName}
                            style={{
                                ...styles.stepItem,
                                color: isActive ? "#2563EB" : isDone ? "#16A34A" : "#94A3B8",
                                fontWeight: isActive ? "bold" : "normal",
                            }}
                        >
                            <div
                                style={{
                                    ...styles.stepCircle,
                                    backgroundColor: isActive
                                        ? "#2563EB"
                                        : isDone
                                        ? "#16A34A"
                                        : "#E2E8F0",
                                    color: isActive || isDone ? "#fff" : "#475569",
                                }}
                            >
                                {isDone ? "✓" : stepNum}
                            </div>
                            <span>{stepName}</span>
                        </div>
                    );
                })}
            </div>

            {errorMessage && <div style={styles.errorBanner}>{errorMessage}</div>}

            <main style={styles.card}>
                {currentStep === 1 && (
                    <div>
                        <h2>Step 1: Upload Your Resume</h2>
                        <p style={{ color: "#64748B" }}>
                            Upload your resume in PDF, DOCX, DOC, or TXT. Scanned files will be parsed with OCR automatically.
                        </p>
                        <form onSubmit={handleUploadResume} style={{ marginTop: "24px" }}>
                            <input
                                type="file"
                                accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg,.bmp"
                                onChange={(e) => setResumeFile(e.target.files[0])}
                                style={styles.fileInput}
                                required
                            />
                            <button
                                type="submit"
                                disabled={!resumeFile || loading}
                                style={styles.primaryBtn}
                            >
                                {loading ? "Parsing & structuring profile..." : "Upload & Continue ->"}
                            </button>
                        </form>
                    </div>
                )}

                {currentStep === 2 && (
                    <div>
                        <h2>Step 2: Extracted Profile & Target Job Description</h2>
                        <p style={{ color: "#64748B" }}>
                            Profile parsed for: <strong>{resumeData?.name || "Candidate"}</strong>
                        </p>

                        <div style={styles.chipBox}>
                            <strong>Extracted Skills:</strong>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "8px" }}>
                                {resumeData?.skills?.map((skill) => (
                                    <span key={skill} style={styles.skillChip}>{skill}</span>
                                ))}
                            </div>
                        </div>

                        <div style={{ marginTop: "20px" }}>
                            <label><strong>Target Job Role:</strong></label>
                            <input
                                type="text"
                                value={targetRole}
                                onChange={(e) => setTargetRole(e.target.value)}
                                style={styles.inputField}
                            />
                        </div>

                        <div style={{ marginTop: "16px" }}>
                            <label><strong>Paste Job Description (JD):</strong></label>
                            <textarea
                                rows={6}
                                value={jdText}
                                onChange={(e) => setJDText(e.target.value)}
                                placeholder="Paste the target job description here..."
                                style={styles.textarea}
                            />
                        </div>

                        <div style={styles.actionsRow}>
                            <button onClick={() => setCurrentStep(1)} style={styles.secondaryBtn}>Back</button>
                            <button
                                onClick={handleAnalyzeJD}
                                disabled={!jdText.trim() || loading}
                                style={styles.primaryBtn}
                            >
                                {loading ? "Matching semantics..." : "Run Match & Skill Gap Analysis ->"}
                            </button>
                        </div>
                    </div>
                )}

                {currentStep === 3 && (
                    <div>
                        <h2>Step 3: Semantic Match & Skill Gap Diagnostics</h2>

                        <div style={styles.metricsGrid}>
                            <div style={styles.metricCard}>
                                <span style={{ fontSize: "14px", color: "#64748B" }}>Semantic Match</span>
                                <span style={{ display: "block", marginTop: "8px", fontSize: "28px", fontWeight: "bold", color: "#2563EB" }}>
                                    {matchResult?.semantic_match_percentage ?? 0}%
                                </span>
                            </div>
                            <div style={styles.metricCard}>
                                <span style={{ fontSize: "14px", color: "#64748B" }}>Readiness Score</span>
                                <span style={{ display: "block", marginTop: "8px", fontSize: "28px", fontWeight: "bold", color: "#16A34A" }}>
                                    {gapResult?.readiness_score ?? matchResult?.skill_coverage_percentage ?? 0}%
                                </span>
                            </div>
                        </div>

                        <div style={{ marginTop: "20px" }}>
                            <h4 style={{ color: "#16A34A", marginBottom: "10px" }}>Matched Skills</h4>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                                {(gapResult?.required?.matched || matchResult?.matched_skills || []).map((skill) => (
                                    <span
                                        key={skill}
                                        style={{
                                            ...styles.skillChip,
                                            background: "#DCFCE7",
                                            color: "#166534",
                                        }}
                                    >
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <div style={styles.actionsRow}>
                            <button onClick={() => setCurrentStep(2)} style={styles.secondaryBtn}>Back</button>
                            <button onClick={handleFetchImprovementsAndRoadmaps} disabled={loading} style={styles.primaryBtn}>
                                {loading ? "Synthesizing AI fixes..." : "Generate AI Fixes & Roadmaps ->"}
                            </button>
                        </div>
                    </div>
                )}

                {currentStep === 4 && (
                    <div>
                        <h2>Step 4: AI Resume Improvements & Learning Paths</h2>

                        {improvementError && (
                            <div style={styles.errorBanner} role="alert">
                                Resume improvements unavailable: {improvementError}
                            </div>
                        )}

                        {improvements?.ats_score_estimate != null && (
                            <p><strong>Estimated ATS Score:</strong> {improvements.ats_score_estimate}/100</p>
                        )}

                        {improvements?.formatting_fixes?.length > 0 && (
                            <>
                                <h3>Formatting Fixes</h3>
                                <ul>{improvements.formatting_fixes.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
                            </>
                        )}

                        {improvements?.missing_section_alerts?.length > 0 && (
                            <>
                                <h3>Missing Sections</h3>
                                <ul>{improvements.missing_section_alerts.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
                            </>
                        )}

                        <h3>Target Bullet Improvements (Google XYZ Format):</h3>
                        {improvements?.bullet_improvements?.length ? (
                            improvements.bullet_improvements.slice(0, 3).map((item, idx) => (
                                <div key={idx} style={styles.bulletBox}>
                                    <div style={{ color: "#DC2626" }}><strong>Before:</strong> {item.original}</div>
                                    <div style={{ color: "#16A34A", marginTop: "4px" }}><strong>Optimized:</strong> {item.improved}</div>
                                    {item.reason && (
                                        <small style={{ color: "#64748B", display: "block", marginTop: "4px" }}>
                                            Why: {item.reason}
                                        </small>
                                    )}
                                </div>
                            ))
                        ) : (
                            <p>{improvementError ? "Add an OpenAI API key and generate again to get tailored bullet rewrites." : "No bullet rewrites were returned for this resume."}</p>
                        )}

                        {improvements?.keyword_integrated_advice?.length > 0 && (
                            <>
                                <h3>Keyword Integration</h3>
                                <ul>{improvements.keyword_integrated_advice.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
                            </>
                        )}

                        <h3 style={{ marginTop: "24px" }}>Recommended Learning Paths for Gaps:</h3>
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "10px" }}>
                            {recommendations.map((rec, i) => (
                                <div key={i} style={styles.recCard}>
                                    <strong>{rec.skill}:</strong> {rec.topic}
                                    <div style={{ fontSize: "12px", color: "#64748B", marginTop: "4px" }}>
                                        Project: {rec.recommended_project}
                                    </div>
                                </div>
                            ))}
                        </div>
                        {recommendations.length === 0 && <p>No learning paths were returned for the identified skill gaps.</p>}

                        <div style={styles.actionsRow}>
                            <button onClick={() => setCurrentStep(3)} style={styles.secondaryBtn}>Back</button>
                            <button onClick={handleStartInterview} style={styles.primaryBtn}>
                                Proceed to AI Mock Interview 
                            </button>
                        </div>
                    </div>
                )}

                {currentStep === 5 && (
                    <div>
                        <h2>Step 5: AI Technical Mock Interview</h2>
                        <p style={{ color: "#64748B" }}>
                            Practice answering this role-tailored technical scenario:
                        </p>

                        <div style={styles.questionBox}>
                            <strong>Question:</strong> {interviewQuestion}
                        </div>

                        <div style={{ marginTop: "16px" }}>
                            <label><strong>Your Answer:</strong></label>
                            <textarea
                                rows={5}
                                value={userAnswer}
                                onChange={(e) => setUserAnswer(e.target.value)}
                                placeholder="Explain the technical concepts, architecture and measurable results..."
                                style={styles.textArea}
                            />
                        </div>

                        <div style={styles.actionsRow}>
                            <button onClick={() => setCurrentStep(4)} style={styles.secondaryBtn}>Back</button>
                            <button
                                onClick={handleSubmitInterview}
                                disabled={!userAnswer.trim() || loading}
                                style={styles.primaryBtn}
                            >
                                {loading ? "Scoring answer..." : "Submit Answer & View Growth ->"}
                            </button>
                        </div>
                    </div>
                )}

                {currentStep === 6 && (
                    <div>
                        <h2>Step 6: Performance Feedback & Career Growth</h2>

                        {interviewFeedback && (
                            <div style={styles.metricCard}>
                                <h3>Interview Score: {interviewFeedback.score}/100</h3>
                                <p><strong>Strengths:</strong> {interviewFeedback.strengths?.join(", ")}</p>
                                <p><strong>Areas to Improve:</strong> {interviewFeedback.areas_for_improvement?.join(", ")}</p>
                                <div style={{ background: "#F1F5F9", padding: "10px", borderRadius: "6px" }}>
                                    <strong>Example Answer:</strong> {interviewFeedback.examplar_model_answer}
                                </div>
                            </div>
                        )}

                        <h3 style={{ marginTop: "24px" }}>Adjacent Roles Matching Your Profile:</h3>
                        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                            {careerPaths.map((path, idx) => (
                                <div key={idx} style={styles.pathBadge}>
                                    <strong>{path.role}</strong>
                                    <span style={{ color: "#2563EB", marginLeft: "6px" }}>{path.match_percentage}%</span>
                                </div>
                            ))}
                        </div>

                        {analytics && (
                            <p style={{ marginTop: "16px", color: "#64748B" }}>
                                Total Revision Logged: <strong>{analytics.total_iterations}</strong> | Average Interview Score: <strong>{analytics.average_interview_score}</strong>
                            </p>
                        )}

                        <div style={styles.actionsRow}>
                            <button
                                onClick={() => {
                                    setCurrentStep(1);
                                    setErrorMessage("");
                                    setResumeFile(null);
                                    setResumeId("");
                                    setResumeData(null);
                                    setResumeText("");
                                    setTargetRole("Software Engineer");
                                    setJDText("");
                                    setMatchResult(null);
                                    setGapResult(null);
                                    setImprovements(null);
                                    setRecommendations([]);
                                    setUserAnswer("");
                                    setInterviewFeedback(null);
                                    setCareerPaths([]);
                                    setAnalytics(null);
                                }}
                                style={styles.primaryBtn}
                            >
                                Restart New Evaluation
                            </button>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

const styles = {
    container: {
        maxWidth: "900px",
        margin: "30px auto",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        color: "#1E293B",
    },
    header: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "24px",
    },
    badge: {
        background: "#DCFCE7",
        color: "#166534",
        padding: "4px 10px",
        borderRadius: "20px",
        fontSize: "12px",
        fontWeight: "600",
    },
    stepperContainer: {
        display: "flex",
        justifyContent: "space-between",
        padding: "14px 20px",
        borderRadius: "10px",
        marginBottom: "24px",
        border: "1px solid #E2E8F0",
    },
    stepItem: {
        display: "flex",
        alignItems: "center",
        gap: "8px",
        fontSize: "13px",
    },
    stepCircle: {
        width: "24px",
        height: "24px",
        borderRadius: "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "12px",
        fontWeight: "bold",
    },
    card: {
        background: "#FFFFFF",
        padding: "32px",
        borderRadius: "12px",
        border: "1px solid #E2E8F0",
        boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
    },
    fileInput: {
        display: "block",
        marginBottom: "20px",
        fontSize: "14px",
    },
    inputField: {
        width: "100%",
        padding: "10px",
        borderRadius: "6px",
        border: "1px solid #CBD5E1",
        marginTop: "6px",
        boxSizing: "border-box",
    },
    textarea: {
        width: "100%",
        padding: "10px",
        borderRadius: "6px",
        border: "1px solid #CBD5E1",
        marginTop: "6px",
        boxSizing: "border-box",
        fontFamily: "inherit",
    },
    textArea: {
        width: "100%",
        padding: "10px",
        borderRadius: "6px",
        border: "1px solid #CBD5E1",
        marginTop: "6px",
        boxSizing: "border-box",
        fontFamily: "inherit",
    },
    primaryBtn: {
        background: "#2563EB",
        color: "#FFFFFF",
        padding: "10px 18px",
        border: "none",
        borderRadius: "6px",
        fontWeight: "600",
        cursor: "pointer",
    },
    secondaryBtn: {
        background: "#E2E8F0",
        color: "#334155",
        padding: "10px 18px",
        border: "none",
        borderRadius: "6px",
        fontWeight: "600",
        cursor: "pointer",
    },
    actionsRow: {
        display: "flex",
        justifyContent: "space-between",
        marginTop: "24px",
    },
    chipBox: {
        background: "#F8FAFC",
        padding: "12px",
        borderRadius: "8px",
        marginTop: "16px",
    },
    skillChip: {
        background: "#E2E8F0",
        color: "#334155",
        padding: "4px 10px",
        borderRadius: "4px",
        fontSize: "12px",
    },
    metricsGrid: {
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "16px",
        margin: "20px 0",
    },
    metricCard: {
        background: "#F8FAFC",
        border: "1px solid #E2E8F0",
        padding: "16px",
        borderRadius: "8px",
    },
    bulletBox: {
        borderLeft: "3px solid #2563EB",
        background: "#F8FAFC",
        padding: "10px 14px",
        margin: "8px 0",
        borderRadius: "0 6px 6px 0",
    },
    recCard: {
        border: "1px solid #E2E8F0",
        padding: "10px",
        borderRadius: "6px",
        background: "#FFFFFF",
    },
    questionBox: {
        background: "#EFF6FF",
        borderLeft: "4px solid #2563EB",
        padding: "14px",
        borderRadius: "4px",
        margin: "12px 0",
    },
    pathBadge: {
        border: "1px solid #CBD5E1",
        padding: "8px 14px",
        borderRadius: "6px",
        background: "#F8FAFC",
    },
    errorBanner: {
        background: "#FEE2E2",
        color: "#991B1B",
        padding: "10px 14px",
        borderRadius: "6px",
        marginBottom: "16px",
        fontSize: "14px",
    },
};