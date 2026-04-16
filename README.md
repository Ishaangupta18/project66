# MathTrack — Weekly Feedback and Learning Analytics

**Live application:** https://mathtrack.streamlit.app

MathTrack is a web-based tool designed to support weekly teaching and learning in Mathematics for Computing. It allows students to rate their understanding of each week's topic and complete a short quiz, then shows both students and teachers how self-reported understanding relates to actual quiz performance over time.

---

## What Problem Does This Solve?

Student feedback on teaching is typically collected at the end of a module — by which point it is too late to benefit the current cohort. Even when feedback is collected regularly, it captures only how students *feel* about their understanding, not how well they can actually apply the material.

MathTrack addresses this by collecting both signals in the same weekly interaction: a short feedback form followed by a topic quiz. By storing them as a single linked record, the system can compute a **Perception Gap** — the difference between how well a student thought they understood a topic and how well they actually performed. This gap can highlight topics where students are overconfident or underconfident, giving both students and teachers an earlier, more actionable picture of learning progress.

---

## How to Use the Application

### For Students

1. Go to https://mathtrack.streamlit.app
2. Select **Student** from the role dropdown and enter your Student ID
3. In the **Weekly Submission** tab:
   - Choose the topic you studied that week
   - Rate the clarity, pace, and difficulty of the teaching using the sliders
   - Add any optional comments
   - Click **Submit Feedback**
4. Once feedback is submitted, the quiz for that topic unlocks automatically
5. Answer the three multiple-choice questions and click **Submit Quiz**
6. Visit the **My Progress** tab to see your full submission history, average scores, and a chart comparing your perceived understanding against your actual quiz performance over time

### For Teachers

1. Go to https://mathtrack.streamlit.app
2. Select **Teacher** from the role dropdown and enter the teacher password
3. The **Class Overview** tab shows total submissions, unique students, and topics covered, with a bar chart comparing perceived and actual scores across all topics
4. The **Topic Analysis** tab lets you select a specific topic and view detailed charts and submission records for that topic only
5. The **Export Data** tab lets you download the full submissions dataset as a CSV file for further analysis in Excel or any other tool

---

## Technology

| Component | Tool | Purpose |
|-----------|------|---------|
| Web framework | Streamlit (Python) | Builds the interactive interface without requiring separate front-end code |
| Data storage | Google Sheets (via gspread API) | Persistent cloud storage that survives server redeployments |
| Data analysis | pandas | Loads and filters submission records |
| Visualisation | Altair | Produces charts with proper axis labels, tooltips, and consistent colour coding |
| Deployment | Streamlit Community Cloud | Free public hosting; accessible from any browser without installation |
| Version control | Git / GitHub | Full commit history documents every development decision |

---

## Running Locally

**Requirements:** Python 3.10 or higher

```bash
# 1. Clone the repository
git clone https://github.com/Ishaangupta18/project66.git
cd project66

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up secrets
# Create a file at .streamlit/secrets.toml with your Google service account
# credentials (see docs/setup-guide.md for details)

# 5. Run the application
streamlit run app.py
```

The app will open automatically at http://localhost:8501

---

## Project Structure

```
project66/
├── app.py                  Main application — all logic in a single file
├── requirements.txt        Python package dependencies with pinned versions
├── .gitignore              Excludes virtual environment and secrets from Git
├── README.md               This file
└── .streamlit/
    └── secrets.toml        Google credentials — NOT committed to Git
```

---

## Data Storage

Submission records are stored in a Google Sheet titled **MathTrack Submissions**. Each row represents one complete student interaction and contains nine fields: timestamp, student ID, topic, clarity rating, pace rating, difficulty rating, optional comments, quiz score, and quiz total.

The Google Sheets backend was chosen over local file storage because Streamlit Community Cloud uses an ephemeral server filesystem — any file written to disk is deleted whenever the application restarts. Storing data in Google Sheets ensures records persist permanently and are accessible independently of server state.

---

## Analytical Measures

**Perceived Score (0–5):** A composite score derived from the three feedback sliders. Pace is adjusted so that the ideal mid-point rating (3 = "just right") contributes the highest score; extreme values in either direction are penalised. Difficulty is inverted so that an easy-difficulty rating contributes a higher score. The formula is:

```
pace_adjusted       = 5 − |pace − 3| × 2
difficulty_adjusted = 6 − difficulty
perceived_score     = (clarity + pace_adjusted + difficulty_adjusted) / 3
```

**Actual Score (0–5):** The student's quiz result scaled from its raw fraction to the 0–5 range so it can be compared directly with the perceived score on the same axis.

**Perception Gap:** The signed difference between perceived score and actual score. A positive gap indicates the student felt more confident than their quiz result suggests; a negative gap indicates the opposite.

---

## Limitations

- **Authentication:** The teacher password is a hardcoded string. The student login accepts any non-empty string as a valid ID. Both would need to be replaced with institutional authentication (e.g. university single sign-on) before any real deployment.
- **Storage throughput:** The Google Sheets API has rate limits that would cause failures under simultaneous high-volume writes. A relational database would be required for production use.
- **Dataset size:** The system has been tested with a small sample dataset. No statistical claims about learning trends can be made from this data.
- **Quiz bank:** Five questions per topic, with three selected randomly per session. Students who repeat the same topic will begin to see repeated questions after two sessions.

---

## Academic Context

This application was developed as the software artefact for COMP6013 Computing Honours Project at Oxford Brookes University (2025–26). The project explores the relationship between students' self-reported understanding of weekly mathematics topics and their actual performance on short topic quizzes, using a Design Science Research methodology.

**Supervisor:** Lucia  
**Student:** Ishaan  
**Module:** COMP6013 Computing Honours Project
