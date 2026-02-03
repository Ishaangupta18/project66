import streamlit as st

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
