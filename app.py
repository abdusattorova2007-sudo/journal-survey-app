import json
from datetime import datetime
import streamlit as st

st.set_page_config(
    page_title="Academic Journal Survey",
    page_icon="📘",
    layout="centered"
)

VERSION = "1.0"

TOPIC = "Academic Journal Keeping and Personal Insight Development Survey for University Students"

QUESTIONS = [
    "How often do you write about your academic experiences in a journal?",
    "How often do you reflect on what you learned during the day?",
    "How often do you record your thoughts about academic challenges?",
    "How often do you write about your feelings related to studying?",
    "How often do you review your journal entries to understand your progress?",
    "How often does journaling help you identify your academic strengths?",
    "How often does journaling help you notice your academic weaknesses?",
    "How often do you use journal writing to set personal academic goals?",
    "How often do you gain new personal insights while writing in your journal?",
    "How often does journaling help you understand your emotions better?",
    "How often do your journal entries help you improve your study habits?",
    "How often do you write honestly about your academic mistakes?",
    "How often do you connect your journal reflections to future improvement?",
    "How often does journaling help you manage academic stress?",
    "How often do you feel that journal keeping is meaningful for your personal development?"
]

OPTIONS = {
    "Always": 0,
    "Often": 1,
    "Sometimes": 2,
    "Rarely": 3,
    "Never": 4
}

PSYCHOLOGICAL_STATES = {
    "Excellent journal practice and strong insight development": (0, 12),
    "Good reflective habit and useful personal insight": (13, 24),
    "Moderate journaling and developing self-awareness": (25, 36),
    "Limited journaling and weak insight development": (37, 48),
    "Very low journaling engagement and minimal reflective insight": (49, 60)
}


def validate_name(name: str) -> bool:
    name = name.strip()
    return len(name) >= 2 and not any(ch.isdigit() for ch in name)


def validate_student_id(student_id: str) -> bool:
    return student_id.isdigit() and len(student_id) >= 4


def validate_dob(date_text: str) -> bool:
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def interpret_score(total_score: int) -> str:
    for state, (low, high) in PSYCHOLOGICAL_STATES.items():
        if low <= total_score <= high:
            return state
    return "Unknown state"


def get_recommendation(result_state: str) -> str:
    recommendations = {
        "Excellent journal practice and strong insight development":
            "You show a very strong habit of academic reflection. Continue journaling regularly and use it to maintain progress.",
        "Good reflective habit and useful personal insight":
            "You have a healthy journaling pattern. Keep writing consistently and deepen your reflections with more detail.",
        "Moderate journaling and developing self-awareness":
            "You use journaling sometimes, but not consistently. Try to write more regularly and focus on lessons learned.",
        "Limited journaling and weak insight development":
            "Your current journal habit is limited. Start with short entries after study sessions and reflect on challenges and feelings.",
        "Very low journaling engagement and minimal reflective insight":
            "You may benefit from beginning a simple academic journal. Write a few sentences daily about what you learned, felt, and plan to improve."
    }
    return recommendations.get(result_state, "No recommendation available.")


def build_result_record(given_name, surname, dob, student_id, selected_answers):
    total_score = sum(OPTIONS[answer] for answer in selected_answers)
    result_state = interpret_score(total_score)
    recommendation = get_recommendation(result_state)

    answers = []
    for i, answer in enumerate(selected_answers, start=1):
        answers.append({
            "question_number": i,
            "question_text": QUESTIONS[i - 1],
            "selected_option_text": answer,
            "score": OPTIONS[answer]
        })

    return {
        "version": VERSION,
        "topic": TOPIC,
        "completion_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "student": {
            "given_name": given_name.strip(),
            "surname": surname.strip(),
            "date_of_birth": dob.strip(),
            "student_id": student_id.strip()
        },
        "total_score": total_score,
        "result_state": result_state,
        "recommendation": recommendation,
        "score_ranges": PSYCHOLOGICAL_STATES,
        "answers": answers
    }


st.title("📘 Academic Journal Survey")
st.subheader("Academic Journal Keeping and Personal Insight Development Survey for University Students")

st.markdown("**Author:** Feruzaxon Abdusattorova")
st.markdown("**Course:** Fundamentals of Programming")

st.markdown(
    """
This web application collects responses about academic journal keeping and personal insight development.
Please complete all fields and answer all 15 questions honestly.

**Scoring note:** lower scores indicate stronger journal keeping and deeper reflective insight.
"""
)

with st.expander("See score interpretation"):
    st.write("0–12: Excellent journal practice and strong insight development")
    st.write("13–24: Good reflective habit and useful personal insight")
    st.write("25–36: Moderate journaling and developing self-awareness")
    st.write("37–48: Limited journaling and weak insight development")
    st.write("49–60: Very low journaling engagement and minimal reflective insight")

with st.form("survey_form"):
    st.markdown("### Student information")
    given_name = st.text_input("Given name")
    surname = st.text_input("Surname")
    dob = st.text_input("Date of birth (YYYY-MM-DD)")
    student_id = st.text_input("Student ID (digits only)")

    st.markdown("### Survey questions")

    selected_answers = []
    option_labels = list(OPTIONS.keys())

    for index, question in enumerate(QUESTIONS, start=1):
        answer = st.radio(
            f"Q{index}. {question}",
            option_labels,
            index=None,
            key=f"q_{index}"
        )
        selected_answers.append(answer)

    submitted = st.form_submit_button("Submit survey")

if submitted:
    errors = []

    if not validate_name(given_name):
        errors.append("Given name is invalid. Use at least 2 letters and no digits.")
    if not validate_name(surname):
        errors.append("Surname is invalid. Use at least 2 letters and no digits.")
    if not validate_dob(dob):
        errors.append("Date of birth must be in YYYY-MM-DD format.")
    if not validate_student_id(student_id):
        errors.append("Student ID must contain only digits and be at least 4 digits long.")
    if any(answer is None for answer in selected_answers):
        errors.append("Please answer all 15 questions.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        record = build_result_record(given_name, surname, dob, student_id, selected_answers)

        st.success("Survey submitted successfully.")
        st.markdown("## Result")
        st.write(f"**Total score:** {record['total_score']}")
        st.write(f"**Result state:** {record['result_state']}")
        st.info(record["recommendation"])

        json_text = json.dumps(record, indent=4, ensure_ascii=False)

        st.download_button(
            label="Download result as JSON",
            data=json_text,
            file_name=f"{student_id}_journal_survey_result.json",
            mime="application/json"
        )

        text_lines = [
            TOPIC,
            "=" * 70,
            f"Version: {record['version']}",
            f"Date and time: {record['completion_time']}",
            f"Given name: {record['student']['given_name']}",
            f"Surname: {record['student']['surname']}",
            f"Date of birth: {record['student']['date_of_birth']}",
            f"Student ID: {record['student']['student_id']}",
            "=" * 70,
            f"Total score: {record['total_score']}",
            f"Result: {record['result_state']}",
            f"Recommendation: {record['recommendation']}",
            "=" * 70,
            "Answers:"
        ]

        for answer in record["answers"]:
            text_lines.append("")
            text_lines.append(f"Question {answer['question_number']}: {answer['question_text']}")
            text_lines.append(f"Chosen answer: {answer['selected_option_text']}")
            text_lines.append(f"Score: {answer['score']}")

        text_content = "\n".join(text_lines)

        st.download_button(
            label="Download result as TXT",
            data=text_content,
            file_name=f"{student_id}_journal_survey_result.txt",
            mime="text/plain"
        )
