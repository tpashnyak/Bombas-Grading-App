# Bombas Grading Studio — NO-API edition

This Streamlit web app grades the **seven Bombas Topic 1.1 case-study questions** in three modes: manual scoring, **rule-based draft grading without an API key**, and optional OpenAI-assisted draft grading. Teachers make the final decision for every score and comment. The scoring criteria come from the user-supplied Bombas handout and teaching note. The rubric is teacher-developed, not an official College Board rubric.

## A. Update an existing GitHub / Streamlit app — easiest

If Bombas Grading Studio is **already on GitHub** and Streamlit is **already deployed**:

1. Download `Bombas_NoAPI_GitHub_Update.zip` and **extract** it on your computer.
2. Open your repository: `https://github.com/tpashnyak/Bombas-Grading-App` (or your actual repository).
3. Verify you are on branch `main`, and that `app.py`, `grader.py`, `rubric_data.py`, and `rubric_pdf.py` appear in the repository's top-level file list.
4. Click **Add file → Upload files**. Upload the **three files inside the extracted update package**, namely `app.py`, `rule_grader.py`, and `README.md`. GitHub can update existing files that have the same name.
5. Enter a commit message such as `Add free rule-based grading without API`, then **Commit changes** to the appropriate branch (or use a pull request if your repository requires it).
6. Return to your existing Streamlit app and refresh. Streamlit Community Cloud normally updates the app automatically when you commit changes to the connected GitHub branch. You should now see **Suggest grades + feedback (NO API)**.
7. If it does not update, verify your Streamlit app is using repository `tpashnyak/Bombas-Grading-App`, branch `main`, and main file `app.py` in the repository root; look at **Manage app → Logs** for errors.

**Do not upload the ZIP itself as the app.** GitHub must contain individual Python files. Do not put the files inside an extra subfolder if Streamlit expects `app.py` at the repository root.

## B. First-time Streamlit deployment

1. Download `Bombas_Grading_Studio_NoAPI_Complete.zip`, then extract its contents.
2. Create a GitHub repository and upload all files **inside** `Bombas_Grading_App/` to the repository root.
3. Visit https://share.streamlit.io and sign in with GitHub. Select **Create app** and your repository.
4. Enter **Branch: `main`** (or the branch your repository actually uses) and **Main file path: `app.py`**.
5. Deploy the app. No OpenAI API key or payment account is needed for the offline rule-based grading engine.

## C. Teacher workflow

1. Upload a `.docx` Word document or **searchable** `.pdf` student assignment. Scanned PDFs need OCR before use.
2. Select the uploaded student's file and verify the seven automatically detected answers. You can correct or paste answers in the seven text boxes if the file formatting confused the parser.
3. Click **🔎 Suggest grades + feedback (NO API)**. This analyzes extracted text within the running Streamlit app; it makes **no OpenAI API request**.
4. Review the suggested 100-point scores, each criterion's comment, the teacher response, and the next-step question. Correct misleading scores and write your own feedback where needed, especially for creative or nuanced student work.
5. Check the teacher-review approval box, then click **Download one-page completed rubric (PDF)** to print.
6. Alternatively, use the completely **Manual grading** option without an upload. The sidebar also offers the blank, fillable PDF.

## Grading criteria / points

| Question | Rubric criterion | Points |
| --- | --- | ---: |
| R1 | Business and products | 10 |
| R2 | People and stakeholders | 15 |
| R3 | Opportunity or challenge | 10 |
| P1 | Target paying customer | 15 |
| P2 | Market gap | 15 |
| P3 | Market/technical research and problem-solution fit | 20 |
| A1 | Product improvement proposal | 15 |
| **Total** | | **100** |

## Limitations and privacy

**Rule-based grading is not AI.** The no-API system uses question headings and transparent concept/keyword patterns to generate **preliminary suggestions**. It can miss synonyms, reward irrelevant keyword use, misinterpret negation, and cannot reliably assess critical thinking, originality, or the strength of an explanation. In particular, the application question receives a conservative *provisional* score; the teacher must evaluate it personally. The teacher can change every score, comment, and feedback field before issuing a final grade. Student work is not saved to files by the application code, but uploading to a publicly reachable Streamlit instance still transfers the work to that hosting service. Use only test or institution-approved data until privacy and access-control requirements are addressed.

Optional AI assistance requires your own OpenAI API key and may incur separate charges. Do not commit credentials to GitHub or use identifiable student work with third-party AI services without institution approval.

The app reads only selectable text in `.docx` and `.pdf` (no handwriting recognition, OCR, LMS connections, gradebook sync, or batch export). Grading is per student file in the current browser session. Print-ready completed PDFs are separate from the blank AcroForm template.

## Files

- `app.py` — Streamlit interface; upload, preview, draft buttons, teacher review, export.
- `rule_grader.py` — local rule-based grading engine and answer splitter; no API access.
- `grader.py` — extraction of DOCX/PDF plus **optional** OpenAI grading.
- `rubric_data.py` — teacher-developed rubric and answer-key elements.
- `rubric_pdf.py` — one-page printable PDF generator.
- `Bombas_Fillable_Rubric.pdf` — editable one-page blank PDF.
- `requirements.txt` — Python dependencies for Streamlit deployment.
- `START_HERE_Windows.bat` — run the full app locally on Windows, if desired.

For local use, extract the full ZIP and double-click `START_HERE_Windows.bat`. Python 3.10+ is required for local use; Streamlit hosting installs it for you.
