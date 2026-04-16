import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import csv
from pathlib import Path
from datetime import datetime
import pandas as pd
import random
import altair as alt

# Settings

TEACHER_PASSWORD   = "teacher123"

QUESTIONS_PER_QUIZ = 3

# Consistent colours used across all charts.
# Blue = perceived understanding, Orange = actual quiz score.
COLOUR_PERCEIVED = "#4C72B0"
COLOUR_ACTUAL    = "#DD8452"


# Quiz bank
# Each topic has 5 questions. Every session, 3 are picked at random so
# students who repeat a topic see some variety.

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
            "options": ["2x3 matrix", "3x2 matrix", "2x2 matrix", "3x3 matrix"],
            "answer": "2x3 matrix"
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
            "q": "lim(x -> 0) x equals…",
            "options": ["0", "1", "infinity", "undefined"],
            "answer": "0"
        },
        {
            "q": "lim(x -> a) c, where c is a constant, equals…",
            "options": ["0", "c", "a", "undefined"],
            "answer": "c"
        },
        {
            "q": "For a limit to exist at a point, the left-hand and right-hand limits must be…",
            "options": ["different", "both zero", "equal", "infinite"],
            "answer": "equal"
        },
        {
            "q": "lim(x -> infinity) 1/x equals…",
            "options": ["1", "infinity", "0", "undefined"],
            "answer": "0"
        },
        {
            "q": "L'Hopital's rule is used when a limit takes an indeterminate form such as…",
            "options": ["0/0", "1/infinity", "infinity + 1", "0 x 1"],
            "answer": "0/0"
        },
    ],
    "Derivatives": [
        {
            "q": "The derivative of x squared is…",
            "options": ["2x", "x", "x cubed", "2"],
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
            "q": "If events A and B are independent, P(A and B) equals…",
            "options": ["P(A) + P(B)", "P(A) x P(B)", "P(A) - P(B)", "0"],
            "answer": "P(A) x P(B)"
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

@st.cache_resource
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope
    )
    client = gspread.authorize(creds)
    return client.open("MathTrack Submissions").sheet1
# Data functions

def save_submission(student_id, topic, clarity, pace, difficulty,
                    comments, quiz_score, quiz_total):
    sheet = get_sheet()
    sheet.append_row([
        datetime.now().isoformat(timespec="seconds"),
        student_id, topic, clarity, pace, difficulty,
        comments, quiz_score, quiz_total
    ])


def load_data():
    sheet = get_sheet()
    records = sheet.get_all_records()
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["student_id"] = (
        df["student_id"].fillna("").astype(str)
        .str.replace(r"\.0$", "", regex=True).str.strip()
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def compute_scores(df):
    """
    Adds perceived_score and actual_score columns.

    perceived_score (0-5):
        Combines clarity, pace, and difficulty into a single composite.
        Pace is adjusted so that the ideal mid-point (3) scores highest.
        Difficulty is inverted so a student who found the topic easy gets
        a higher contribution to the perceived score.

        perceived_score = (clarity + pace_adjusted + difficulty_adjusted) / 3
        where:
            pace_adjusted       = 5 - |pace - 3| x 2
            difficulty_adjusted = 6 - difficulty

    actual_score (0-5):
        Quiz result scaled from its raw fraction to the 0-5 range so it
        can be plotted on the same axis as perceived_score.
    """
    df = df.copy()
    df["pace_adjusted"]       = df["pace"].apply(lambda x: 5 - abs(x - 3) * 2)
    df["difficulty_adjusted"] = 6 - df["difficulty"]
    df["perceived_score"] = (
        df["clarity"] + df["pace_adjusted"] + df["difficulty_adjusted"]
    ) / 3
    df["actual_score"] = (df["quiz_score"] / df["quiz_total"]) * 5
    return df


# Chart helpers
# Using Altair so that every chart has proper titles, axis labels,
# a consistent colour scheme, and interactive tooltips.

def line_chart(df, title):
    """
    Builds a labelled Altair line chart comparing perceived and actual
    scores over time. Dots are drawn at each data point.
    Expects df to have columns: timestamp, perceived_score, actual_score.
    """
    # Altair works best with tidy (long-format) data, so we reshape the table.
    long = df[["timestamp", "perceived_score", "actual_score"]].melt(
        id_vars="timestamp", var_name="Measure", value_name="Score"
    )
    long["Measure"] = long["Measure"].map({
        "perceived_score": "Perceived Understanding",
        "actual_score":    "Actual (Quiz) Score"
    })

    chart = (
        alt.Chart(long)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X(
                "timestamp:T",
                title="Submission Date",
                axis=alt.Axis(labelAngle=-30, format="%d %b")
            ),
            y=alt.Y(
                "Score:Q",
                title="Score  (0 - 5 scale)",
                scale=alt.Scale(domain=[0, 5])
            ),
            color=alt.Color(
                "Measure:N",
                scale=alt.Scale(
                    domain=["Perceived Understanding", "Actual (Quiz) Score"],
                    range=[COLOUR_PERCEIVED, COLOUR_ACTUAL]
                ),
                legend=alt.Legend(title="", orient="bottom")
            ),
            tooltip=[
                alt.Tooltip("timestamp:T",  title="Date",    format="%d %b %Y"),
                alt.Tooltip("Measure:N",    title="Measure"),
                alt.Tooltip("Score:Q",      title="Score",   format=".2f"),
            ]
        )
        .properties(title=title, width="container")
    )
    return chart


def bar_chart(perceived, actual, title):
    """
    Builds a labelled Altair bar chart comparing two average scores.
    """
    data = pd.DataFrame({
        "Measure": ["Perceived Understanding", "Actual (Quiz) Score"],
        "Score":   [round(perceived, 2), round(actual, 2)]
    })

    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        .encode(
            x=alt.X("Measure:N", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(
                "Score:Q",
                title="Average Score  (0 - 5 scale)",
                scale=alt.Scale(domain=[0, 5])
            ),
            color=alt.Color(
                "Measure:N",
                scale=alt.Scale(
                    domain=["Perceived Understanding", "Actual (Quiz) Score"],
                    range=[COLOUR_PERCEIVED, COLOUR_ACTUAL]
                ),
                legend=None
            ),
            tooltip=[
                alt.Tooltip("Measure:N", title="Measure"),
                alt.Tooltip("Score:Q",   title="Score", format=".2f")
            ]
        )
        .properties(title=title, width="container")
    )
    return chart


def show_formula():
    """
    Displays the perceived score formula inside a collapsible section.
    """
    with st.expander("How is the Perceived Score calculated?"):
        st.markdown(
            "The **Perceived Score** is a composite measure on a 0-5 scale "
            "that summarises how a student experienced a topic in a given week. "
            "It is computed from three feedback ratings:"
        )
        st.latex(
            r"\text{Perceived Score} = "
            r"\frac{C + P' + D'}{3}"
        )
        st.markdown("Where:")
        st.markdown(
            "- **C** = Clarity rating (1-5, student's rating of how clearly the topic was taught)\n"
            "- **P'** = Adjusted Pace = $5 - |\\text{Pace} - 3| \\times 2$  "
            "  *(rewards a pace rating of 3 — the ideal — and penalises extremes)*\n"
            "- **D'** = Adjusted Difficulty = $6 - \\text{Difficulty}$  "
            "  *(inverted so that an easy topic contributes a higher score)*"
        )
        st.markdown(
            "The **Actual Score** is the student's quiz result "
            "scaled to the same 0-5 range:  "
            "$\\text{Actual Score} = \\dfrac{\\text{Quiz Score}}{\\text{Total Questions}} \\times 5$"
        )


# Page configuration (must be the first Streamlit call)

st.set_page_config(
    page_title="MathTrack",
    page_icon="📐",
    layout="centered"
)


# Session state
# Variables that must survive a page rerun are stored here.

DEFAULTS = {
    "logged_in":            False,
    "user_role":            None,
    "logged_in_student_id": "",
    "feedback_submitted":   False,
    "feedback_data":        {},
    "quiz_questions":       [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# Login screen

if not st.session_state["logged_in"]:

    st.title("MathTrack")
    st.subheader("Weekly Feedback & Learning Analytics")
    st.markdown(
        "MathTrack supports weekly reflection on mathematics topics. "
        "Students rate their understanding and complete a short quiz each week. "
        "Teachers can track trends and identify topics that may need revisiting."
    )

    with st.expander("How does MathTrack work?"):
        st.markdown(
            "**For students — three simple steps each week:**\n\n"
            "1. Log in with your Student ID.\n"
            "2. Rate how clearly the topic was taught, the pace, and how difficult you found it.\n"
            "3. Complete a short three-question quiz on the same topic.\n\n"
            "Your results are saved and shown back to you on the **My Progress** page "
            "so you can see how your understanding develops over time.\n\n"
            "**For teachers:**  \n"
            "Log in with the teacher password to access the class overview and "
            "topic-level dashboards showing perceived and actual understanding across the class."
        )

    st.divider()

    login_role = st.selectbox("I am a…", ["Student", "Teacher"])

    if login_role == "Student":
        student_login_id = st.text_input("Enter your Student ID")
        if st.button("Log in", type="primary"):
            if student_login_id.strip():
                st.session_state["logged_in"]            = True
                st.session_state["user_role"]            = "Student"
                st.session_state["logged_in_student_id"] = student_login_id.strip()
                st.rerun()
            else:
                st.warning("Please enter your Student ID before logging in.")

    else:
        teacher_pwd = st.text_input("Enter Teacher Password", type="password")
        if st.button("Log in", type="primary"):
            if teacher_pwd == TEACHER_PASSWORD:
                st.session_state["logged_in"]  = True
                st.session_state["user_role"]  = "Teacher"
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

    st.stop()


# Shared header (visible after login)

role = st.session_state["user_role"]

col_title, col_logout = st.columns([4, 1])
with col_title:
    if role == "Student":
        st.title("MathTrack — Student View")
        st.caption(f"Logged in as: **{st.session_state['logged_in_student_id']}**")
    else:
        st.title("MathTrack — Teacher View")
        st.caption("Logged in as: **Teacher**")

with col_logout:
    st.write("")
    if st.button("Log out"):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()


# Student view

if role == "Student":

    tab_submit, tab_progress = st.tabs(["Weekly Submission", "My Progress"])

    # Tab 1: Feedback form and quiz

    with tab_submit:

        st.header("Step 1 — Weekly Feedback")
        st.markdown(
            "Rate how teaching went for the topic you studied this week. "
            "Submitting this will unlock the quiz below."
        )

        if not st.session_state["feedback_submitted"]:
            with st.form("feedback_form"):
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
                    placeholder="e.g. I found integration by parts particularly tricky…"
                )
                submit_feedback = st.form_submit_button(
                    "Submit Feedback & Unlock Quiz", type="primary"
                )

            if submit_feedback:
                chosen = random.sample(QUIZ_BANK[topic],
                                       min(QUESTIONS_PER_QUIZ, len(QUIZ_BANK[topic])))
                st.session_state["quiz_questions"]     = chosen
                st.session_state["feedback_submitted"] = True
                st.session_state["feedback_data"] = {
                    "student_id": st.session_state["logged_in_student_id"],
                    "topic": topic, "clarity": clarity,
                    "pace": pace, "difficulty": difficulty, "comments": comments,
                }
                st.rerun()

        else:
            fb = st.session_state["feedback_data"]
            st.success(
                f"Feedback submitted for **{fb['topic']}**. "
                "Complete the quiz below to save your record."
            )

        # Quiz

        if st.session_state["feedback_submitted"]:
            st.divider()
            st.header("Step 2 — Topic Quiz")
            fb        = st.session_state["feedback_data"]
            questions = st.session_state["quiz_questions"]
            st.markdown(
                f"Answer the three questions below about **{fb['topic']}**. "
                "Your score will be saved together with your feedback."
            )

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
                score = sum(
                    1 for i, item in enumerate(questions)
                    if user_answers[i] == item["answer"]
                )
                save_submission(
                    fb["student_id"], fb["topic"], fb["clarity"], fb["pace"],
                    fb["difficulty"], fb["comments"], score, len(questions)
                )
                # Clear session state so the form resets for next week.
                st.session_state["feedback_submitted"] = False
                st.session_state["feedback_data"]      = {}
                st.session_state["quiz_questions"]     = []

                st.success(f"Submitted! Your score: **{score} / {len(questions)}**")
                st.subheader("Answer Review")
                for i, item in enumerate(questions, start=1):
                    correct = item["answer"]
                    chosen  = user_answers[i - 1]
                    if chosen == correct:
                        st.write(f"Q{i}: Correct — *{correct}*")
                    else:
                        st.write(
                            f"Q{i}: You chose *{chosen}* — "
                            f"correct answer: **{correct}**"
                        )

    # Tab 2: My Progress

    with tab_progress:

        st.header("My Learning Progress")
        st.markdown(
            "The charts below compare your **perceived understanding** "
            "(derived from your weekly feedback ratings) with your "
            "**actual quiz performance** across all submissions."
        )

        show_formula()

        df_all = load_data()
        sid    = st.session_state["logged_in_student_id"]

        if df_all.empty or sid not in df_all["student_id"].values:
            st.info(
                "No submissions yet — complete a Weekly Submission first "
                "to start tracking your progress."
            )
        else:
            student_df = compute_scores(
                df_all[df_all["student_id"] == sid].copy()
            ).sort_values("timestamp")

            st.subheader("Submission History")
            st.dataframe(
                student_df[
                    ["timestamp", "topic", "clarity", "pace",
                     "difficulty", "quiz_score", "quiz_total"]
                ].rename(columns={
                    "timestamp":  "Date / Time", "topic":      "Topic",
                    "clarity":    "Clarity",     "pace":       "Pace",
                    "difficulty": "Difficulty",  "quiz_score": "Quiz Score",
                    "quiz_total": "Out Of"
                }),
                width="stretch"
            )

            st.subheader("Overall Summary")
            avg_p = student_df["perceived_score"].mean()
            avg_a = student_df["actual_score"].mean()
            gap   = avg_p - avg_a

            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Perceived Score", f"{avg_p:.2f} / 5")
            col2.metric("Avg Actual Score",    f"{avg_a:.2f} / 5")
            col3.metric(
                "Perception Gap",
                f"{gap:+.2f}",
                help="Positive = perceived understanding is higher than actual quiz score. "
                     "Negative = actual score is higher than perceived understanding."
            )

            st.subheader("Scores Over Time")
            st.altair_chart(
                line_chart(student_df, "Perceived vs Actual Understanding Over Time")
            )

            st.subheader("Overall Average Comparison")
            st.altair_chart(
                bar_chart(avg_p, avg_a, "Average Perceived vs Actual Score")
            )


# Teacher view

if role == "Teacher":

    tab_overview, tab_topic, tab_export = st.tabs(
        ["Class Overview", "Topic Analysis", "Export Data"]
    )

    df_all = load_data()

    if df_all.empty:
        for tab in [tab_overview, tab_topic, tab_export]:
            with tab:
                st.info(
                    "No submissions recorded yet. "
                    "Students need to complete at least one Weekly Submission first."
                )
        st.stop()

    df_scored = compute_scores(df_all)

    # Tab 1: Class Overview

    with tab_overview:

        st.header("Class Overview")
        st.markdown("A high-level summary of all student submissions across all topics.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Submissions", len(df_all))
        col2.metric("Unique Students",   df_all["student_id"].nunique())
        col3.metric("Topics Covered",    df_all["topic"].nunique())

        st.subheader("Recent Submissions")
        st.dataframe(
            df_all.sort_values("timestamp", ascending=False).head(20),
            width="stretch"
        )

        st.subheader("Average Scores by Topic")
        topic_summary = (
            df_scored.groupby("topic")
            .agg(
                Submissions   = ("student_id",     "count"),
                Avg_Clarity   = ("clarity",         "mean"),
                Avg_Perceived = ("perceived_score", "mean"),
                Avg_Actual    = ("actual_score",    "mean"),
            )
            .round(2)
            .rename(columns={
                "Avg_Clarity":   "Avg Clarity",
                "Avg_Perceived": "Avg Perceived Score",
                "Avg_Actual":    "Avg Actual Score"
            })
        )
        st.dataframe(topic_summary, width="stretch")

        show_formula()

    # Tab 2: Topic Analysis

    with tab_topic:

        st.header("Topic-Level Analysis")

        selected_topic = st.selectbox(
            "Choose a topic to analyse",
            df_all["topic"].unique().tolist()
        )

        topic_df = compute_scores(
            df_all[df_all["topic"] == selected_topic].copy()
        ).sort_values("timestamp")

        if topic_df.empty:
            st.info("No data for this topic yet.")
        else:
            avg_clarity    = topic_df["clarity"].mean()
            avg_difficulty = topic_df["difficulty"].mean()
            avg_quiz_pct   = (topic_df["quiz_score"] / topic_df["quiz_total"]).mean() * 100
            avg_perceived  = topic_df["perceived_score"].mean()
            avg_actual     = topic_df["actual_score"].mean()

            st.subheader(f"Summary — {selected_topic}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Submissions",    len(topic_df))
            c2.metric("Avg Clarity",    f"{avg_clarity:.2f} / 5")
            c3.metric("Avg Difficulty", f"{avg_difficulty:.2f} / 5")
            c4.metric("Avg Quiz Score", f"{avg_quiz_pct:.1f}%")

            st.subheader("Perceived vs Actual Understanding")
            st.caption(
                "Perceived score is derived from the feedback ratings. "
                "Actual score is the quiz result scaled to 0-5."
            )
            st.altair_chart(
                bar_chart(
                    avg_perceived, avg_actual,
                    f"Average Scores — {selected_topic}"
                )
            )

            gap = avg_perceived - avg_actual
            if abs(gap) < 0.3:
                st.success(
                    "Perception and performance are well aligned for this topic."
                )
            elif gap > 0:
                st.warning(
                    f"On average, students overestimate their understanding "
                    f"by **{gap:.2f} points**. "
                    "Consider revisiting this topic in a future session."
                )
            else:
                st.info(
                    f"On average, students underestimate their understanding "
                    f"by **{abs(gap):.2f} points**. "
                    "Confidence-building activities may help."
                )

            st.subheader("Trend Over Time")
            st.altair_chart(
                line_chart(topic_df, f"Score Trend — {selected_topic}")
            )

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
                    "perceived_score": "Perceived Score",
                    "actual_score":    "Actual Score"
                }),
                width="stretch"
            )

    # Tab 3: Export

    with tab_export:

        st.header("Export Submission Data")
        st.markdown(
            "Download the full dataset as a CSV file. "
            "This can be opened in Excel or any spreadsheet application "
            "for further analysis."
        )
        csv_bytes = df_all.to_csv(index=False).encode("utf-8")
        filename  = f"mathtrack_submissions_{datetime.now().strftime('%Y%m%d')}.csv"

        st.download_button(
            label     = "Download all submissions as CSV",
            data      = csv_bytes,
            file_name = filename,
            mime      = "text/csv",
            type      = "primary"
        )
        st.caption(
            f"Dataset contains **{len(df_all)} submissions** "
            f"from **{df_all['student_id'].nunique()} student(s)**."
        )