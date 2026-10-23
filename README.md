# Bombas Grading Studio — teacher guide

This is a **working local Streamlit application** for scoring the seven questions in the uploaded Bombas case materials. The **blank one-page PDF** is fillable in a standard PDF editor such as Adobe Acrobat Reader and can also be printed for handwriting. The app makes a **separate, print-ready completed PDF** after teacher review. It is not hosted online; run or deploy the app yourself.

## What you receive

- `Bombas_Fillable_Rubric.pdf`: editable one-page 100-point rubric, with student/teacher/date fields, seven score/quick-comment boxes, total score, teacher response, and a revision prompt.
- `app.py`: Streamlit user interface for upload, AI draft grading, manual overrides, feedback editing, and print-ready PDF export.
- `grader.py`: `.pdf`/`.docx` text extraction and optional AI assessment against the supplied teaching-note evidence.
- `rubric_data.py`, `rubric_pdf.py`: scoring framework and PDF rendering.

## Windows setup

1. Install **Python 3.10 or newer** from https://www.python.org/downloads/ if needed. During installation, enable *Add Python to PATH*.
2. Unzip this project into a folder (do not run directly from the ZIP).
3. Double-click `START_HERE_Windows.bat`. It creates a local virtual environment, installs the packages, and starts the local app in your browser. This initial setup needs an Internet connection.
4. For future launches, run the batch file again. It may check the packages before starting.

## macOS or Linux setup

Run in the unzipped project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app normally opens at `http://localhost:8501`. Stop it with Ctrl+C in the terminal.

## Teacher workflow

1. Upload one or more student's Word (`.docx`) or searchable PDF (`.pdf`) files. Choose the submission to grade, or choose the **Manual grading** option.
2. Inspect extracted text to ensure all responses were captured. Image-based scans require OCR first; Word images and handwriting are not parsed.
3. Without an API key, type scores and feedback yourself. **Optional AI:** enter your personal/institution-authorized **OpenAI API key** in the sidebar and click **Draft all seven scores + teacher response with AI**. API usage may incur separate charges.
4. Review evidence, scores, and comments against the actual student submission. Correct any mistakes. AI drafts should not be automatically treated as final grades.
5. Edit the personal teacher response and next-step prompt. Confirm teacher review, then download a **one-page print-ready PDF**.
6. Repeat for other uploaded files; the app tracks entries per file during the current browser session.

## Scoring design (100 points)

| ID | Criterion | Points |
| --- | --- | ---: |
| R1 | Business and products | 10 |
| R2 | People and stakeholders | 15 |
| R3 | Opportunity or challenge | 10 |
| P1 | Target paying customer | 15 |
| P2 | Market gap | 15 |
| P3 | Research and problem-solution fit | 20 |
| A1 | Product improvement proposal | 15 |

This *teacher-created allocation* is based on the uploaded Bombas reading questions, practice questions, application activity, and teaching note. It is **not** an official College Board rubric.

## Privacy, safety, and deployment

Student work is processed in memory by the app and not written to files by the included code. Streamlit or infrastructure operators may have their own operational/logging practices. When you explicitly click the AI draft button, the app sends the **extracted student text** and the teacher-developed rubric/teaching reference to an OpenAI API model for analysis. The request uses `store=False`. Do not use with student data unless the processing is approved by your institution and complies with its privacy requirements. For greater privacy, choose the fully manual path, which makes no AI request.

**Do not place an API key in source files or publish it in GitHub.** The sidebar password field is session-specific; if deployed, use a server-side secret manager. Safeguard the local machine and access to the app.

The AI response is a **draft**. It may overlook sections, misread tables, make grading mistakes, or be biased. Original work and professional teacher judgment take priority. Incomplete/non-extractable documents should be reviewed manually. The PDF exporter truncates overlong row notes or teacher comments to fit the single page; the app limits character counts to reduce clipping. Check the PDF before printing.

## Customize

- Adjust question weights/criteria and source-aligned teaching notes in `rubric_data.py` (weights should still total 100 unless you revise the form). Recreate the blank template by running `python rubric_pdf.py`.
- Change AI model in the sidebar if your API account has access to another supported model.
- For team-wide use, deploy `app.py` to an institution-approved Streamlit-compatible server. This package is **not** a hosted service and does not include student accounts or an LMS gradebook integration.
