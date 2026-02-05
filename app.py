import streamlit as st

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

with st.form("feedback_form"):
    topic = st.selectbox(
        "Select the topic",
        ["Limits", "Derivatives", "Matrices", "Vectors", "Probability"]
    )

    clarity = st.slider(
        "How clear was the teaching for this topic?",
        min_value=1,
        max_value=5,
        value=3
    )

    pace = st.slider(
        "How was the pace of teaching?",
        min_value=1,
        max_value=5,
        value=3
    )

    difficulty = st.slider(
        "How difficult did you find this topic?",
        min_value=1,
        max_value=5,
        value=3
    )

    comments = st.text_area(
        "Any additional comments (optional)"
    )

    submitted = st.form_submit_button("Submit feedback")

if submitted:
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


quiz_topic = topic  

if quiz_topic in QUIZ_BANK:
    questions = QUIZ_BANK[quiz_topic]

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

        st.success(f"Quiz submitted! Your score: {score}/{len(questions)}")

        st.subheader("Answer review")
        for i, item in enumerate(questions, start=1):
            correct = item["answer"]
            chosen = user_answers[i-1]
            if chosen == correct:
                st.write(f"✅ Q{i}: Correct")
            else:
                st.write(f"❌ Q{i}: You chose '{chosen}'. Correct answer: '{correct}'")
else:
    st.warning("Please select a topic to load the quiz.")
