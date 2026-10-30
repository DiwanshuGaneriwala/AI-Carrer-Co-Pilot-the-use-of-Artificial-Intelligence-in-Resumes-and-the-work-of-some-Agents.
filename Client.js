const API_BASE = "http://localhost:8000/api";

export async function uploadResume(file){
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/resume/upload`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
    }
    return res.json();
}