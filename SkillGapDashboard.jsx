import React from "react";

export default function SkillGapDashboard({ analysisResult }) {
    if (!analysisResult) return null;

    const { readiness_score, required, preferred, additional_candidate_skills } = analysisResult;

    return (
        <div style={{ maxWidth: "650px", margin: "20px auto", fontFamily: "sans-serif" }}>
            <h2>Skill Gap Analysis</h2>
            
            <div style={{ marginBottom: "20px" }}>
                <strong>Role Readiness Score: {readiness_score}%</strong>
                <div style={{ background: "#e0e0e0", borderRadius: "8px", height: "12px", marginTop: "6px" }}>
                    <div
                        style={{
                            width: `${readiness_score}%`,
                            background: readiness_score > 70 ? "#2e7d32" : readiness_score > 40 ? "#ed6c02" : "#d32f2f",
                            height: "100%",
                            borderRadius: "8px",
                            transition: "width 0.4s ease"
                        }}
                    />
                </div>
            </div>

            {/* Critical Required Skills */}
            <div style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "16px", marginBottom: "16px" }}>
                <h3>Required Skills ({required.match_percentage}% Matched)</h3>
                
                <p><strong>Matched:</strong></p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                    {required.matched.length > 0 ? (
                        required.matched.map((skill) => (
                            <span key={skill} style={{ background: "#e8f5e9", color: "#2e7d32", padding: "4px 8px", borderRadius: "4px" }}>
                                ✓ {skill}
                            </span>
                        ))
                    ) : <em>None matched yet</em>}
                </div>

                <p style={{ marginTop: "12px" }}><strong>Missing (Critical Gaps):</strong></p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                    {required.missing.length > 0 ? (
                        required.missing.map((skill) => (
                            <span key={skill} style={{ background: "#ffebee", color: "#c62828", padding: "4px 8px", borderRadius: "4px" }}>
                                ✕ {skill}
                            </span>
                        ))
                    ) : <span>No critical skills missing</span>}
                </div>
            </div>

            {/* Preferred / Nice-to-Have Skills */}
            {preferred && (preferred.matched.length > 0 || preferred.missing.length > 0) && (
                <div style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "16px", marginBottom: "16px" }}>
                    <h3>Preferred Skills ({preferred.match_percentage}% Matched)</h3>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                        {preferred.matched.map((s) => (
                            <span key={s} style={{ background: "#e3f2fd", color: "#1565c0", padding: "4px 8px", borderRadius: "4px" }}>
                                ✓ {s}
                            </span>
                        ))}
                        {preferred.missing.map((s) => (
                            <span key={s} style={{ background: "#f5f5f5", color: "#757575", padding: "4px 8px", borderRadius: "4px" }}>
                                ○ {s}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Extra Skills */}
            {additional_candidate_skills?.length > 0 && (
                <div style={{ padding: "8px 0" }}>
                    <small style={{ color: "#666" }}>
                        <strong>Other Skills on Profile: </strong>
                        {additional_candidate_skills.join(", ")}
                    </small>
                </div>
            )}
        </div>
    );
}