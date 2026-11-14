# 🎓 AI-Based College Enquiry Chatbot

An intelligent, lightweight, and modern College Enquiry Assistant engineered in Python using Natural Language Processing (TF-IDF Vectorization and Cosine Similarity) and Streamlit.

Designed for prospective students, current scholars, and parents to receive verified answers regarding **Courses, Admissions, Fees, Hostel, Library, Placements, Examinations, and Administrative Contacts**.

---

## 📌 Project Overview

Traditional college enquiry methods (physical administrative desks, congested phone helplines, static PDF prospectuses) result in long waiting times and high staff workloads.

The **AI-Based College Enquiry Chatbot (VRBot for VR College of Engineering)** solves this by:
- **ChatGPT-like Friendly Conversational AI**: Communicates naturally and intelligently, using warm, supportive, and polite English with tasteful formatting and emojis.
- **Multi-Turn Memory & Follow-up Understanding**: Remembers conversation context across turns (e.g., student asks *"What courses are available?"* followed by *"Explain the first one"* or *"What is the fee for that?"*).
- **Hybrid AI Architecture**: Integrates **Google Gemini 2.5 Flash** (via `google-genai`) for conversational generation, with an intelligent **Local NLP Conversational Agent** fallback for 100% offline, zero-cost operation without requiring an API key.
- **Strict Grounding (Zero Hallucination)**: Responses are grounded strictly on verified college facts from `college_faq.csv`. Never invents fees or dates.
- **Intelligent Typo-Tolerance & Fuzzy Matching**: Resilient against student spelling mistakes (`admision`, `hostal`, `scolorship`, `plcmnt`, `librari`).
- **Student Admission Lead Capture**: Direct inquiry form generating official reference numbers (`VRCE-26-XXXXX`).
- **Staff & Administrative Desk** (PIN: `admin123`): Real-time analytics, lead tracking, unanswered queries gap tracker, and FAQ CRUD manager.
- **Voice Assistance**: Speech-to-Text voice query input + HTML5 Speech Synthesis audio playback (Read Aloud 🔊).
- **Official Prospectus PDF Download**: One-click download of the complete 2026-27 academic prospectus and fee schedule.

---

## 📂 Project Folder Structure

```
AI_College_Enquiry_Chatbot/
│
├── app.py                      # Modern ChatGPT-style Streamlit User Interface application
├── chatbot.py                  # Core NLP engine (TF-IDF, Cosine Similarity, fuzzy typo matcher)
├── ai_agent.py                 # Gemini LLM integration, multi-turn memory & local friendly generator
├── data_loader.py              # CSV loader, schema validator, and dynamic FAQ CRUD operations
├── lead_manager.py             # Student leads, feedback ratings, and unanswered queries manager
├── college_faq.csv             # Verified FAQ dataset (42+ entries across 10 categories)
├── generate_prospectus.py      # Official academic brochure & prospectus PDF generator
├── requirements.txt            # Python dependencies specification
├── README.md                   # Installation, setup, and usage documentation
│
├── assets/
│   ├── logo.png                # College emblem branding image
│   ├── ui_preview.png          # UI screenshot mockup for documentation & slides
│   └── VR_College_Prospectus_2026.pdf # Official generated prospectus
│
├── documentation/
│   ├── project_report.md       # Complete 20-section mini-project report
│   ├── presentation.pptx       # Professional 12-slide PowerPoint presentation
│   └── viva_questions.md       # 40 comprehensive Viva Voce questions & answers
│
└── tests/
    ├── test_chatbot.py         # Pytest core NLP & conversational intent test suite (26 tests)
    └── test_features.py        # Pytest new features, follow-ups & admin CRUD test suite (7 tests)
```

---

## 💻 Software Requirements

- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** Python 3.10 or higher (Fully tested on Python 3.13)
- **Web Browser:** Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari
- **IDE (Recommended):** Visual Studio Code

---

## ⚙️ Step-by-Step Installation & Setup

### 1. Python Installation
If Python is not already installed on your system:
1. Download Python from [python.org](https://www.python.org/downloads/).
2. Run the installer and **be sure to check the box: "Add Python to PATH"**.
3. Verify installation in PowerShell / Command Prompt:
   ```bash
   python --version
   ```

### 2. VS Code Setup
1. Download and install [Visual Studio Code](https://code.visualstudio.com/).
2. Open VS Code and install the official **Python Extension** by Microsoft.
3. Open the project folder in VS Code:
   `File` ➔ `Open Folder...` ➔ Select `AI_College_Enquiry_Chatbot`.

### 3. Create a Virtual Environment (Recommended)
Open the integrated terminal in VS Code (`Ctrl + ~` or `Terminal` ➔ `New Terminal`) and run:

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Install all required libraries via `pip`:
```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `streamlit` - Interactive web application framework
- `pandas` - Tabular data manipulation and validation
- `scikit-learn` - TF-IDF vectorization and cosine similarity
- `python-pptx` - Programmatic PowerPoint presentation generator
- `pytest` - Automated testing framework
- `pillow` - Image generation and rendering

---

## 🚀 How to Run the Application

Execute the main application using Streamlit:

```bash
streamlit run app.py
```

Streamlit will launch local web server and open the browser automatically at:
```
http://localhost:8501
```

*(If the browser doesn't open automatically, hold `Ctrl` and click the URL printed in the terminal).*

---

## 🤖 Setting Up AI Intelligence (Optional Gemini API)

The chatbot runs **100% offline out-of-the-box** using its intelligent Local Conversational Agent.

To enable ChatGPT-like generative responses with Google Gemini:
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. You can provide the API key in any of three easy ways:
   - **Option A (Interactive UI):** Paste it into the **Google Gemini API Key** field in the sidebar.
   - **Option B (Environment Variable):** Set it in PowerShell:
     ```powershell
     $env:GEMINI_API_KEY="your_api_key_here"
     ```
   - **Option C (.env File):** Create a `.env` file in the project root:
     ```ini
     GEMINI_API_KEY=your_api_key_here
     ```

---

## 🧪 How to Run Automated Tests

To run the complete automated test suite (33 unit and integration tests):

```bash
python -m pytest tests/ -v
```

Expected output:
```
============================= 33 passed in 4.10s ==============================
```

---

## 📊 How to Update the College FAQ Dataset

To customize or replace the demonstration data with your institution's verified information:

1. Open `college_faq.csv` in Excel, Google Sheets, or VS Code.
2. The CSV contains three columns:
   - `category`: The functional topic (e.g. `Courses`, `Admission`, `Fees`, `Hostel`, `Library`, `Placement`, `Contact`).
   - `question`: The standard question or enquiry phrased naturally.
   - `answer`: The official, verified college information response.
3. Add or modify rows as needed.
4. Save the file.
5. In your browser running the Streamlit app, click **"Rerun"** or press `R` on your keyboard. The chatbot will instantly re-index the updated dataset!

---

## 🔧 Troubleshooting Common Errors

### 1. `streamlit : The term 'streamlit' is not recognized...`
- **Cause:** Python Scripts directory is not on the system PATH.
- **Fix:** Run Streamlit through Python directly:
  ```bash
  python -m streamlit run app.py
  ```

### 2. `ModuleNotFoundError: No module named '...'`
- **Cause:** Dependencies were installed in a different environment or not installed yet.
- **Fix:** Run:
  ```bash
  pip install -r requirements.txt
  ```

### 3. `DataLoaderError: Dataset file not found...`
- **Cause:** Running the command from a directory that does not contain `college_faq.csv`.
- **Fix:** Navigate into the project directory before running:
  ```bash
  cd AI_College_Enquiry_Chatbot
  streamlit run app.py
  ```

### 4. Port 8501 is already in use
- **Cause:** Another Streamlit instance is running in the background.
- **Fix:** Run Streamlit on an alternate port:
  ```bash
  streamlit run app.py --server.port 8502
  ```

---

## 👥 Academic Evaluation & Credits

- **Project Title:** AI-Based College Enquiry Chatbot
- **Category:** Mini Project / Capstone Project
- **Domain:** Artificial Intelligence, Natural Language Processing, Machine Learning
- **Documentation:** See `documentation/project_report.md`, `documentation/presentation.pptx`, and `documentation/viva_questions.md`.

