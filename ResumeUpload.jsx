import { useState } from "react";
import { uploadResume } from "./Client.js";

export default function ResumeUpload({ onUploaded }) {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState("idle");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) return;
        setStatus("uploading");
        setError("");
        try{
            const result = await uploadResume(file);
            setStatus("done");
            onUploaded?.(result);
        } catch (err){
            setStatus("error");
            setError(err.message); 
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={(e) => setFile(e.target.files[0])}
            />
            <button type="submit" disabled={!file || status === "uploading"}>
                {status === "uploading" ? "Uploading..." : "Upload Resume"}
            </button>
            {status === "error"&& <p role="alert">{error}</p>}
            {status === "done" && <p>Upload successfully.</p>}
        </form>
    );
}