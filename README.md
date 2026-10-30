# AI Career Co-Pilot

## Requirements

- Python 3.10 or newer
- Node.js 20.19+ or 22.12+
- Tesseract OCR and Poppler on `PATH` for scanned PDF/image OCR
- An OpenAI API key for resume improvements, interview scoring, and career chat

## Install

From the repository root in PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm --prefix my-react-app install
```

Set the API key in the same terminal before launching. The app can start without it, but AI-generated features will return a clear service-unavailable message until it is set:

```powershell
$env:OPENAI_API_KEY = "your-key"
.\run_app.bat
```

The launcher starts the API at `http://127.0.0.1:8000` and the dashboard at `http://localhost:5173`. If using a virtual environment, create it at `venv` so the launcher selects its Python interpreter.

## Run separately

Start the API from the repository root:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Start the dashboard in another terminal:

```powershell
npm --prefix my-react-app run dev -- --host 127.0.0.1
```

Legacy `.doc` parsing requires Pandoc in addition to the Python packages. PDF/image OCR requires the external Tesseract and Poppler executables; regular text-based PDF, DOCX, and TXT parsing does not.
