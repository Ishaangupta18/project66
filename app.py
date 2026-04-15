import streamlit as st
import csv
from pathlib import Path
from datetime import datetime
import pandas as pd
import random

# SETTINGS
# The teacher password is stored here. In a real deployment this would be
# stored as an environment variable, but hardcoding it is fine for a prototype.

TEACHER_PASSWORD = "teacher123"

# Path to the CSV file where all submissions are saved.
DATA_FILE = Path("data/submissions.csv")

# How many questions to show per quiz session (drawn randomly from the bank).
QUESTIONS_PER_QUIZ = 3


# QUIZ BANK
# Each topic has 5 questions. Every time a student takes a quiz, 3 are
# picked at random, so repeat attempts feel slightly different.

QUIZ_BANK = {
    "Vectors": [
        {
            "q": "Which of the following is a valid 2D vector?",
            "options": ["(3, 4)", "3 + 4", "3 / 4", "None of these"],
            "answer": "(3, 4)"
        },
        {
            "q": "What is the magnitude of the vector (3, 4)?",
            "options": ["5", "7", "1", "12"],
            "answer": "5"
        },
        {
            "q": "If a vector is multiplied by a scalar of 2, its magnitude will…",
            "options": ["halve", "double", "stay the same", "become zero"],
            "answer": "double"
        },
        {
            "q": "Which operation produces a scalar from two vectors?",
            "options": ["Dot product", "Cross product", "Vector addition", "Scalar projection"],
            "answer": "Dot product"
        },
        {
            "q": "A unit vector has magnitude equal to…",
            "options": ["0", "1", "2", "it depends on the vector"],
            "answer": "1"
        },
    ],
    "Matrices": [
        {
            "q": "A matrix with 2 rows and 3 columns is called a…",
            "options": ["2×3 matrix", "3×2 matrix", "2×2 matrix", "3×3 matrix"],
            "answer": "2×3 matrix"
        },
        {
            "q": "Which operation is always defined for two matrices of the same size?",
            "options": ["Addition", "Multiplication", "Division", "Square root"],
            "answer": "Addition"
        },
        {
            "q": "The identity matrix has…",
            "options": ["all ones", "ones on the diagonal and zeros elsewhere",
                        "all zeros", "random values"],
            "answer": "ones on the diagonal and zeros elsewhere"
        },
        {
            "q": "Matrix multiplication is defined when the number of columns in A equals…",
            "options": ["the number of rows in B", "the number of columns in B",
                        "the number of rows in A", "the determinant of B"],
            "answer": "the number of rows in B"
        },
        {
            "q": "The transpose of a matrix swaps its…",
            "options": ["rows and columns", "diagonal elements",
                        "signs", "determinant and trace"],
            "answer": "rows and columns"
        },
    ],
    "Limits": [
        {
            "q": "lim(x → 0) x equals…",
            "options": ["0", "1", "infinity", "undefined"],
            "answer": "0"
        },
        {
            "q": "lim(x → a) c, where c is a constant, equals…",
            "options": ["0", "c", "a", "undefined"],
            "answer": "c"
        },
        {
            "q": "For a limit to exist at a point, the left-hand and right-hand limits must be…",
            "options": ["different", "both zero", "equal", "infinite"],
            "answer": "equal"
        },
        {
            "q": "lim(x → ∞) 1/x equals…",
            "options": ["1", "∞", "0", "undefined"],
            "answer": "0"
        },
        {
            "q": "L'Hôpital's rule is used when a limit takes an indeterminate form such as…",
            "options": ["0/0", "1/∞", "∞ + 1", "0 × 1"],
            "answer": "0/0"
        },
    ],
    "Derivatives": [
        {
            "q": "The derivative of x² is…",
            "options": ["2x", "x", "x³", "2"],
            "answer": "2x"
        },
        {
            "q": "A derivative measures…",
            "options": ["area under a curve", "rate of change", "total sum", "y-intercept"],
            "answer": "rate of change"
        },
        {
            "q": "The derivative of a constant is…",
            "options": ["1", "0", "the constant itself", "undefined"],
            "answer": "0"
        },
        {
            "q": "The chain rule is used when differentiating…",
            "options": ["a composite function", "a constant",
                        "a sum of functions", "an integral"],
            "answer": "a composite function"
        },
        {
            "q": "If f'(x) > 0 on an interval, the function is…",
            "options": ["decreasing", "constant", "increasing", "concave down"],
            "answer": "increasing"
        },
    ],
    "Probability": [
        {
            "q": "A valid probability value must lie between…",
            "options": ["-1 and 1", "0 and 1", "0 and 100", "1 and 10"],
            "answer": "0 and 1"
        },
        {
            "q": "If events A and B are independent, P(A ∩ B) equals…",
            "options": ["P(A) + P(B)", "P(A) × P(B)", "P(A) – P(B)", "0"],
            "answer": "P(A) × P(B)"
        },
        {
            "q": "The probability of an impossible event is…",
            "options": ["1", "0", "0.5", "it depends"],
            "answer": "0"
        },
        {
            "q": "Bayes' theorem relates…",
            "options": [
                "conditional and marginal probabilities",
                "independent events only",
                "sample size and variance",
                "cumulative distribution functions"
            ],
            "answer": "conditional and marginal probabilities"
        },
        {
            "q": "The sum of all probabilities in a sample space equals…",
            "options": ["0", "0.5", "1", "it depends on the number of outcomes"],
            "answer": "1"
        },
    ],
}

# DATA FUNCTIONS
# These two functions handle reading and writing the CSV file.


def save_submission(student_id, topic, clarity, pace, difficulty,
                    comments, quiz_score, quiz_total):
    """
    Saves one student's feedback + quiz result as a single row in the CSV.
    Creates the file and the 'data' folder if they don't exist yet.
    """
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_exists = DATA_FILE.exists()
    with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write the header row only the first time the file is created.
        if not file_exists:
            writer.writerow([
                "timestamp", "student_id", "topic",
                "clarity", "pace", "difficulty", "comments",
                "quiz_score", "quiz_total"
            ])
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            student_id, topic, clarity, pace, difficulty,
            comments, quiz_score, quiz_total
        ])


def load_data():
    """
    Loads all submissions from the CSV into a pandas DataFrame.
    Also cleans up the student_id column so filtering works reliably
    (removes accidental spaces or '.0' that can appear after CSV round-trips).
    Returns an empty DataFrame if no data exists yet.
    """
    if not DATA_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)

    # Clean the student_id column so "S001", "S001 ", and "S001.0" all match.
    df["student_id"] = (
        df["student_id"]
        .fillna("")
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def compute_scores(df):
    """
    Adds two computed columns to a DataFrame:

    - perceived_score: a 0–5 composite that combines how clear, well-paced,
      and manageable the student found the topic.
      * pace is adjusted so that 3 (ideal) scores highest and 1 or 5 score lowest.
      * difficulty is inverted so an easy topic (low score) gives a high contribution.

    - actual_score: the quiz result scaled to 0–5 so it can be plotted alongside
      the perceived score on the same axis.
    """
    df = df.copy()
    df["pace_adjusted"]       = df["pace"].apply(lambda x: 5 - abs(x - 3) * 2)
    df["difficulty_adjusted"] = 6 - df["difficulty"]
    df["perceived_score"] = (
        df["clarity"] + df["pace_adjusted"] + df["difficulty_adjusted"]
    ) / 3
    df["actual_score"] = (df["quiz_score"] / df["quiz_total"]) * 5
    return df


# Must be the first Streamlit call in the script.

st.set_page_config(
    page_title="MathTrack",
    page_icon="📐",
    layout="centered"
)

# SESSION STATE INITIALISATION
# Streamlit reruns the whole script on every user interaction, so any variable
# that needs to persist between interactions must live in st.session_state.

defaults = {
    "logged_in": False,
    "user_role": None,
    "logged_in_student_id": "",
    "feedback_submitted": False,
    "feedback_data": {},
    "quiz_questions": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# LOGIN SCREEN
# Shown to everyone who is not yet logged in.

if not st.session_state["logged_in"]:

    st.title("📐 MathTrack")
    st.subheader("Weekly Feedback & Learning Analytics")
    st.markdown(
        "MathTrack helps students reflect on their weekly understanding of "
        "mathematics topics and lets teachers monitor learning trends across the class."
    )
    st.divider()

    login_role = st.selectbox("I am a…", ["Student", "Teacher"])

    if login_role == "Student":
        student_login_id = st.text_input("Enter your Student ID")
        if st.button("Log in", type="primary"):
            if student_login_id.strip():
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Student"
                st.session_state["logged_in_student_id"] = student_login_id.strip()
                st.rerun()
            else:
                st.warning("Please enter your Student ID before logging in.")

    else:  # Teacher login
        teacher_pwd = st.text_input("Enter Teacher Password", type="password")
        if st.button("Log in", type="primary"):
            if teacher_pwd == TEACHER_PASSWORD:
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Teacher"
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

    # Stop here — don't render the rest of the app until the user logs in.
    st.stop()


# Displays the app name, who is logged in, and a logout button.

role = st.session_state["user_role"]

col_title, col_logout = st.columns([4, 1])

with col_title:
    if role == "Student":
        st.title("📐 MathTrack — Student View")
        st.caption(f"Logged in as: **{st.session_state['logged_in_student_id']}**")
    else:
        st.title("📐 MathTrack — Teacher View")
        st.caption("Logged in as: **Teacher**")

with col_logout:
    st.write("")  # small spacer so the button lines up nicely
    if st.button("Log out"):
        # Clear all session state and return to the login screen.
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()


# STUDENT VIEW
if role == "Student":

    # Two tabs: one for submitting this week's feedback + quiz,
    # one for viewing the student's own progress over time.
    tab_submit, tab_progress = st.tabs(["📝 Weekly Submission", "📊 My Progress"])

    # TAB 1 — Weekly Submission (Feedback form + Quiz)
    with tab_submit:

        st.header("Step 1 — Weekly Feedback")
        st.markdown(
            "Rate how teaching went for the topic you studied this week. "
            "Submitting this unlocks the short quiz below."
        )

        # Only show the feedback form if the student hasn't submitted it yet
        # this session. Once submitted, show a confirmation message instead.
        if not st.session_state["feedback_submitted"]:

            with st.form("feedback_form"):
                # Show the student's ID as a read-only field.
                st.text_input(
                    "Student ID",
                    value=st.session_state["logged_in_student_id"],
                    disabled=True
                )

                topic = st.selectbox(
                    "Which topic did you study this week?",
                    list(QUIZ_BANK.keys())
                )

                st.markdown("---")

                st.markdown("**How clear was the teaching for this topic?**")
                st.caption("1 = very unclear  ·  5 = very clear")
                clarity = st.slider("Clarity", 1, 5, 3, label_visibility="collapsed")

                st.markdown("**How was the pace of teaching?**")
                st.caption("1 = too slow  ·  3 = just right  ·  5 = too fast")
                pace = st.slider("Pace", 1, 5, 3, label_visibility="collapsed")

                st.markdown("**How difficult did you find this topic?**")
                st.caption("1 = very easy  ·  5 = very difficult")
                difficulty = st.slider("Difficulty", 1, 5, 3, label_visibility="collapsed")

                comments = st.text_area(
                    "Any additional comments? (optional)",
                    placeholder="e.g. I struggled with the second example in class…"
                )

                submit_feedback = st.form_submit_button(
                    "Submit Feedback & Unlock Quiz", type="primary"
                )

            if submit_feedback:
                # Randomly select 3 questions from the 5 available for this topic.
                all_questions = QUIZ_BANK[topic]
                chosen_questions = random.sample(
                    all_questions, min(QUESTIONS_PER_QUIZ, len(all_questions))
                )

                # Store the selected questions and feedback data in session state
                # so they are still available when the quiz is submitted.
                st.session_state["quiz_questions"] = chosen_questions
                st.session_state["feedback_submitted"] = True
                st.session_state["feedback_data"] = {
                    "student_id": st.session_state["logged_in_student_id"],
                    "topic": topic,
                    "clarity": clarity,
                    "pace": pace,
                    "difficulty": difficulty,
                    "comments": comments,
                }
                st.rerun()

        else:
            # Feedback already submitted this session — show a summary.
            fb = st.session_state["feedback_data"]
            st.success(
                f"Feedback submitted for **{fb['topic']}**. "
                "Now complete the quiz below."
            )

        # Quiz (only visible after feedback is submitted)
        if st.session_state["feedback_submitted"]:

            st.divider()
            st.header("Step 2 — Topic Quiz")
            fb = st.session_state["feedback_data"]
            st.markdown(
                f"Answer the three questions below about **{fb['topic']}**. "
                "Your score will be saved together with your feedback."
            )

            questions = st.session_state["quiz_questions"]

            with st.form("quiz_form"):
                user_answers = []
                for i, item in enumerate(questions, start=1):
                    choice = st.radio(
                        f"**Q{i}.** {item['q']}",
                        item["options"],
                        key=f"quiz_{fb['topic']}_{i}"
                    )
                    user_answers.append(choice)

                submit_quiz = st.form_submit_button("Submit Quiz", type="primary")

            if submit_quiz:
                # Count correct answers.
                score = sum(
                    1 for i, item in enumerate(questions)
                    if user_answers[i] == item["answer"]
                )

                # Save the combined feedback + quiz record to the CSV.
                save_submission(
                    student_id=fb["student_id"],
                    topic=fb["topic"],
                    clarity=fb["clarity"],
                    pace=fb["pace"],
                    difficulty=fb["difficulty"],
                    comments=fb["comments"],
                    quiz_score=score,
                    quiz_total=len(questions),
                )

                # Reset session state so the form is ready for next week.
                st.session_state["feedback_submitted"] = False
                st.session_state["feedback_data"] = {}
                st.session_state["quiz_questions"] = []

                st.success(f"Submitted! Your score: **{score} / {len(questions)}**")

                # Show which answers were right and wrong.
                st.subheader("Answer Review")
                for i, item in enumerate(questions, start=1):
                    correct = item["answer"]
                    chosen  = user_answers[i - 1]
                    if chosen == correct:
                        st.write(f"✅ **Q{i}:** Correct — *{correct}*")
                    else:
                        st.write(
                            f"❌ **Q{i}:** You chose *{chosen}* — "
                            f"correct answer: **{correct}**"
                        )

    # TAB 2 — My Progress
    # Shows the student's own submission history and charts.
    
    with tab_progress:

        st.header("My Learning Progress")
        st.markdown(
            "This page compares your **perceived understanding** "
            "(based on your clarity, pace, and difficulty ratings) "
            "with your **actual quiz performance** over time."
        )

        df_all = load_data()
        sid    = st.session_state["logged_in_student_id"]

        # Check whether this student has any saved submissions.
        if df_all.empty or sid not in df_all["student_id"].values:
            st.info(
                "No submissions found yet. "
                "Complete a Weekly Submission first to start tracking your progress."
            )
        else:
            # Filter to only this student's rows and compute the scores.
            student_df = compute_scores(
                df_all[df_all["student_id"] == sid].copy()
            ).sort_values("timestamp")

            # Submission history table
            st.subheader("Submission History")
            display_cols = ["timestamp", "topic", "clarity", "pace",
                            "difficulty", "quiz_score", "quiz_total"]
            st.dataframe(
                student_df[display_cols].rename(columns={
                    "timestamp":   "Date / Time",
                    "topic":       "Topic",
                    "clarity":     "Clarity",
                    "pace":        "Pace",
                    "difficulty":  "Difficulty",
                    "quiz_score":  "Quiz Score",
                    "quiz_total":  "Out Of"
                }),
                width="stretch"
            )

            # Summary metric cards
            st.subheader("Overall Summary")
            avg_perceived = student_df["perceived_score"].mean()
            avg_actual    = student_df["actual_score"].mean()
            gap           = avg_perceived - avg_actual

            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Perceived Score", f"{avg_perceived:.2f} / 5")
            col2.metric("Avg Actual Score",    f"{avg_actual:.2f} / 5")
            col3.metric("Perception Gap",      f"{gap:+.2f}")

            # Charts
            st.subheader("Perceived vs Actual Understanding Over Time")
            st.caption(
                "Perceived score = average of clarity + adjusted pace + adjusted difficulty. "
                "Actual score = quiz result scaled to 0–5."
            )
            chart_df = student_df.set_index("timestamp")[
                ["perceived_score", "actual_score"]
            ].rename(columns={
                "perceived_score": "Perceived Understanding",
                "actual_score":    "Actual (Quiz) Score"
            })
            st.line_chart(chart_df)

            summary_bar = pd.DataFrame({
                "Type":  ["Perceived Understanding", "Actual (Quiz) Score"],
                "Score": [avg_perceived, avg_actual]
            }).set_index("Type")
            st.bar_chart(summary_bar)


# TEACHER VIEW
if role == "Teacher":

    # Three tabs: a class-wide overview, a per-topic deep dive, and a data export.
    tab_overview, tab_topic, tab_export = st.tabs(
        ["📋 Class Overview", "🔍 Topic Analysis", "⬇️ Export Data"]
    )

    # Load all submissions once and reuse across all three tabs.
    df_all = load_data()

    # If no data exists yet, show a message in every tab and stop.
    if df_all.empty:
        for tab in [tab_overview, tab_topic, tab_export]:
            with tab:
                st.info(
                    "No submissions recorded yet. "
                    "Students need to complete at least one Weekly Submission first."
                )
        st.stop()

    # Pre-compute scores so we don't repeat the calculation in each tab.
    df_scored = compute_scores(df_all)

    # TAB 1 — Class Overview

    with tab_overview:

        st.header("Class Overview")
        st.markdown("A high-level summary of all student submissions.")

        # Top-line metrics.
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Submissions", len(df_all))
        col2.metric("Unique Students",   df_all["student_id"].nunique())
        col3.metric("Topics Covered",    df_all["topic"].nunique())

        # Most recent 20 submissions across all students.
        st.subheader("Recent Submissions")
        st.dataframe(
            df_all.sort_values("timestamp", ascending=False).head(20),
            width="stretch"
        )

        # Per-topic summary: how many submissions, average clarity, and average scores.
        st.subheader("Average Scores by Topic")
        topic_summary = (
            df_scored
            .groupby("topic")
            .agg(
                Submissions    = ("student_id",      "count"),
                Avg_Clarity    = ("clarity",          "mean"),
                Avg_Perceived  = ("perceived_score",  "mean"),
                Avg_Actual     = ("actual_score",     "mean"),
            )
            .round(2)
            .rename(columns={
                "Avg_Clarity":   "Avg Clarity",
                "Avg_Perceived": "Avg Perceived Score",
                "Avg_Actual":    "Avg Actual Score"
            })
        )
        st.dataframe(topic_summary, width="stretch")

    # TAB 2 — Topic Analysis
    with tab_topic:

        st.header("Topic-Level Analysis")

        available_topics = df_all["topic"].unique().tolist()
        selected_topic   = st.selectbox("Choose a topic to analyse", available_topics)

        # Filter and compute scores for the selected topic only.
        topic_df = compute_scores(
            df_all[df_all["topic"] == selected_topic].copy()
        ).sort_values("timestamp")

        if topic_df.empty:
            st.info("No data for this topic yet.")
        else:
            avg_clarity   = topic_df["clarity"].mean()
            avg_difficulty= topic_df["difficulty"].mean()
            avg_quiz_pct  = (topic_df["quiz_score"] / topic_df["quiz_total"]).mean() * 100
            avg_perceived = topic_df["perceived_score"].mean()
            avg_actual    = topic_df["actual_score"].mean()

            # Top-line metrics for the selected topic.
            st.subheader(f"Summary — {selected_topic}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Submissions",    len(topic_df))
            c2.metric("Avg Clarity",    f"{avg_clarity:.2f} / 5")
            c3.metric("Avg Difficulty", f"{avg_difficulty:.2f} / 5")
            c4.metric("Avg Quiz Score", f"{avg_quiz_pct:.1f}%")

            # Perceived vs actual comparison chart.
            st.subheader("Perceived vs Actual Understanding")
            st.caption(
                "Perceived score combines clarity, adjusted pace, and adjusted difficulty. "
                "Actual score is the quiz result scaled to 0–5."
            )
            compare_df = pd.DataFrame({
                "Type":  ["Perceived Understanding", "Actual (Quiz) Score"],
                "Score": [avg_perceived, avg_actual]
            }).set_index("Type")
            st.bar_chart(compare_df)

            # Automatic interpretation of the perception–performance gap.
            # This is one of the core features of the tool.
            gap = avg_perceived - avg_actual
            if abs(gap) < 0.3:
                st.success(
                    "✅ Perception and performance are well aligned for this topic."
                )
            elif gap > 0:
                st.warning(
                    f"⚠️ Students are overestimating their understanding by "
                    f"**{gap:.2f} points** on average. "
                    "This topic may benefit from a follow-up session."
                )
            else:
                st.info(
                    f"ℹ️ Students are underestimating their understanding by "
                    f"**{abs(gap):.2f} points**. "
                    "Confidence-building activities may help here."
                )

            # Trend over time — how perceived and actual scores change week by week.
            st.subheader("Trend Over Time")
            trend_df = topic_df.set_index("timestamp")[
                ["perceived_score", "actual_score"]
            ].rename(columns={
                "perceived_score": "Perceived Understanding",
                "actual_score":    "Actual (Quiz) Score"
            })
            st.line_chart(trend_df)

            # Full submission detail table for this topic.
            st.subheader("All Submissions for This Topic")
            st.dataframe(
                topic_df[[
                    "timestamp", "student_id", "clarity", "pace",
                    "difficulty", "quiz_score", "quiz_total",
                    "perceived_score", "actual_score"
                ]].rename(columns={
                    "timestamp":       "Date / Time",
                    "student_id":      "Student",
                    "clarity":         "Clarity",
                    "pace":            "Pace",
                    "difficulty":      "Difficulty",
                    "quiz_score":      "Quiz Score",
                    "quiz_total":      "Out Of",
                    "perceived_score": "Perceived",
                    "actual_score":    "Actual"
                }),
                width="stretch"
            )

    # TAB 3 — Export Data
    # Lets the teacher download the full dataset as a CSV file.
    with tab_export:

        st.header("Export Submission Data")
        st.markdown(
            "Download the full dataset as a CSV file. "
            "This can be opened in Excel or any spreadsheet application."
        )

        csv_bytes = df_all.to_csv(index=False).encode("utf-8")
        filename  = f"mathtrack_submissions_{datetime.now().strftime('%Y%m%d')}.csv"

        st.download_button(
            label    = "⬇️ Download all submissions as CSV",
            data     = csv_bytes,
            file_name= filename,
            mime     = "text/csv",
            type     = "primary"
        )

        st.caption(
            f"Dataset contains **{len(df_all)} submissions** "
            f"from **{df_all['student_id'].nunique()} student(s)**."
        )