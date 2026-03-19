import streamlit as st
import csv
from pathlib import Path
from datetime import datetime
import pandas as pd

QUIZ_BANK = {
    "Vectors": [
        {
            "q": "Which of these is a valid vector in 2D?",
            "options": ["(3, 4)", "3 + 4", "3/4", "None of these"],
            "answer": "(3, 4)"
        },
        {
            "q": "What is the magnitude of the vector (3, 4)?",
            "options": ["5", "7", "1", "12"],
            "answer": "5"
        },
        {
            "q": "If a vector is multiplied by 2, its magnitude will…",
            "options": ["halve", "double", "stay the same", "become zero"],
            "answer": "double"
        },
    ],
    "Matrices": [
        {
            "q": "A matrix with 2 rows and 3 columns is called…",
            "options": ["2x3", "3×2", "2×2", "3×3"],
            "answer": "2×3"
        },
        {
            "q": "Which operation is always defined for matrices of the same size?",
            "options": ["Addition", "Multiplication", "Division", "Square root"],
            "answer": "Addition"
        },
        {
            "q": "The identity matrix has…",
            "options": ["all ones", "ones on diagonal and zeros elsewhere", "all zeros", "random values"],
            "answer": "ones on diagonal and zeros elsewhere"
        },
    ],
    "Limits": [
        {
            "q": "lim(x→0) x is…",
            "options": ["0", "1", "infinity", "undefined"],
            "answer": "0"
        },
        {
            "q": "lim(x→a) c (constant c) is…",
            "options": ["0", "c", "a", "undefined"],
            "answer": "c"
        },
        {
            "q": "If lim(x→a) f(x) exists, it means the left and right limits are…",
            "options": ["different", "both zero", "equal", "infinite"],
            "answer": "equal"
        },
    ],
    "Derivatives": [
        {
            "q": "The derivative of x^2 is…",
            "options": ["2x", "x", "x^3", "2"],
            "answer": "2x"
        },
        {
            "q": "Derivative measures…",
            "options": ["area under curve", "rate of change", "total sum", "intercept"],
            "answer": "rate of change"
        },
        {
            "q": "Derivative of a constant is…",
            "options": ["1", "0", "the constant", "undefined"],
            "answer": "0"
        },
    ],
    "Probability": [
        {
            "q": "A probability value must be between…",
            "options": ["-1 and 1", "0 and 1", "0 and 100", "1 and 10"],
            "answer": "0 and 1"
        },
        {
            "q": "If events A and B are independent, P(A ∩ B) =",
            "options": ["P(A)+P(B)", "P(A)×P(B)", "P(A)-P(B)", "0"],
            "answer": "P(A)×P(B)"
        },
        {
            "q": "The probability of an impossible event is…",
            "options": ["1", "0", "0.5", "depends"],
            "answer": "0"
        },
    ],
}

DATA_FILE = Path("data/submissions.csv")

def save_submission(student_id: str, topic: str, clarity: int, pace: int, difficulty: int, comments: str, quiz_score: int, quiz_total: int):
    # Ensure the data folder exists
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Create file + header if it doesn't exist
    file_exists = DATA_FILE.exists()
    with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "student_id", "topic", 
                "clarity", "pace", "difficulty",
                "comments",
                "quiz_score", "quiz_total"
            ])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            student_id,
            topic,
            clarity, pace, difficulty,
            comments,
            quiz_score, quiz_total
        ])

st.set_page_config(page_title="Project 66 Prototype", layout="centered")
st.title("Project 66: Weekly Feedback + Quiz Prototype")
st.write("If you can see this page, Streamlit is working ✅")

st.header("Next steps")
st.markdown("""
- Build feedback form
- Add short quiz (MCQs)
- Save results to CSV
- Show simple charts
""")

st.info("Prototype setup complete")

st.divider()
st.header("Weekly Student Feedback")

if "feedback_submitted" not in st.session_state:
    st.session_state["feedback_submitted"] = False

if "feedback_data" not in st.session_state:
    st.session_state["feedback_data"] = {
        "student_id": "",
        "topic": None,
        "clarity": None,
        "pace": None,
        "difficulty": None,
        "comments": ""
    }

with st.form("feedback_form"):
    student_id = st.text_input("Enter Student ID")

    topic = st.selectbox(
        "Select the topic",
        ["Limits", "Derivatives", "Matrices", "Vectors", "Probability"]
    )

    st.write("How clear was the teaching for this topic?")
    st.caption("Scale: 1 = very unclear, 5 = very clear")
    clarity = st.slider(
        "Clarity",
        min_value=1,
        max_value=5,
        value=3,
        label_visibility="collapsed"
    )  

    st.write("How was the pace of teaching?")
    st.caption("Scale: 1 = too slow, 3 = appropriate pace, 5 = too fast")
    pace = st.slider(
        "Pace",
        min_value=1,
        max_value=5,
        value=3,
        label_visibility="collapsed"
    )    

    st.write("How  difficult did you find this topic?")
    st.caption("Scale: 1 = very easy, 5 = very difficult")
    difficulty = st.slider(
        "Difficulty",
        min_value=1,
        max_value=5,
        value=3,
        label_visibility="collapsed"
    )  

    comments = st.text_area(
        "Any additional comments (optional)"
    )
    
    submitted = st.form_submit_button("Submit feedback")

if submitted:
    st.session_state["feedback_submitted"] = True
    st.session_state["feedback_data"] = {
        "student_id" : student_id,
        "topic": topic,
        "clarity": clarity,
        "pace": pace,
        "difficulty": difficulty,
        "comments": comments
    }

    st.success("Feedback submitted successfully!")

    st.subheader("Your feedback summary")
    st.write("Topic:", topic)
    st.write("Clarity score:", clarity)
    st.write("Pace score:", pace)
    st.write("Difficulty score:", difficulty)

    if comments:
        st.write("Comments:", comments)

st.divider()
st.header("Weekly Topic Quiz")
st.write("Answer 3 quick questions based on the selected topic.")

if not st.session_state["feedback_submitted"]:
    st.warning("Please submit feedback first to unlock the quiz.")
    st.stop()

quiz_topic = st.session_state["feedback_data"]["topic"]
questions = QUIZ_BANK.get(quiz_topic, [])

if not questions:
    st.error("No questions found for this topic. Please submit feedback again.")
    st.stop()

with st.form("quiz_form"):
    st.subheader(f"Quiz Topic: {quiz_topic}")

    user_answers = []
    for i, item in enumerate(questions, start=1):
        choice = st.radio(
            f"Q{i}. {item['q']}",
            item["options"],
            key=f"q_{quiz_topic}_{i}"
        )
        user_answers.append(choice)

    quiz_submitted = st.form_submit_button("Submit quiz")

if quiz_submitted:
    score = 0
    for i, item in enumerate(questions):
        if user_answers[i] == item["answer"]:
            score += 1

    fb = st.session_state["feedback_data"]

    save_submission(
        student_id=fb["student_id"],
        topic=fb["topic"],
        clarity=fb["clarity"],
        pace=fb["pace"],
        difficulty=fb["difficulty"],
        comments=fb["comments"],
        quiz_score=score,
        quiz_total=len(questions)
    )

    st.session_state["feedback_submitted"] = False
    st.session_state["feedback_data"] = {
        "student_id": "",
        "topic": None,
        "clarity": None,
        "pace": None,
        "difficulty": None,
        "comments": ""
    }

    st.success(f"Quiz submitted! Your score: {score}/{len(questions)}")

    st.subheader("Answer review")
    for i, item in enumerate(questions, start=1):
        correct = item["answer"]
        chosen = user_answers[i-1]
        if chosen == correct:
            st.write(f"✅ Q{i}: Correct")
        else:
            st.write(f"❌ Q{i}: You chose '{chosen}'. Correct answer: '{correct}'")

st.divider()
st.header("Stored Submissions (Prototype Dashboard)")

if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE)

    st.write("Latest saved records:")
    st.dataframe(df.tail(10), use_container_width=True)

    st.subheader("Topic Analysis")
    selected_topic = st.selectbox("Choose a topic to analyse", df["topic"].unique())

    topic_df = df[df["topic"] == selected_topic].copy()

    topic_df["timestamp"] = pd.to_datetime(topic_df["timestamp"])

    topic_df["pace_adjusted"] = topic_df["pace"].apply(lambda x: 5 - abs(x-3) * 2)

    topic_df["difficulty_adjusted"] = 6 - topic_df["difficulty"]

    topic_df["perceived_score"] = (
        topic_df["clarity"] +
        topic_df["pace_adjusted"] +
        topic_df["difficulty_adjusted"]
    ) / 3

    topic_df["actual_score"] = (topic_df["quiz_score"] / topic_df["quiz_total"]) * 5

    avg_clarity = topic_df["clarity"].mean()
    avg_pace = topic_df["pace"].mean()
    avg_difficulty = topic_df["difficulty"].mean()
    avg_quiz_percent = (topic_df["quiz_score"] / topic_df["quiz_total"]).mean() * 100
    avg_perceived = topic_df["perceived_score"].mean()
    avg_actual = topic_df["actual_score"].mean()
    
    st.subheader("Summary for Selected Topic")
    st.write(f"**Topic:** {selected_topic}")
    st.write(f"**Average clarity:** {avg_clarity:.2f} / 5")
    st.write(f"**Average pace rating:** {avg_pace:.2f} / 5 (ideal pace is 3)")
    st.write(f"**Average difficulty:** {avg_difficulty:.2f} / 5")
    st.write(f"**Average quiz score:** {avg_quiz_percent:.1f}%")
    st.write(f"**Average perceived understanding:** {avg_perceived:.2f} / 5")
    st.write(f"**Average actual understanding:** {avg_actual:.2f} / 5")

    st.subheader("Perceived vs Actual Understanding")
    compare_df = pd.DataFrame({
        "Type": ["Perceived Understanding", "Actual Understanding"],
        "Score": [avg_perceived, avg_actual]
    }).set_index("Type")

    st.bar_chart(compare_df)

    st.subheader("Trend Over Time")
    trend_df = topic_df.sort_values("timestamp")[["timestamp", "perceived_score", "actual_score"]]
    trend_df = trend_df.set_index("timestamp")

    st.line_chart(trend_df)

else:
    st.info("No submissions saved yet. Submit feedback + quiz to create the CSV.")