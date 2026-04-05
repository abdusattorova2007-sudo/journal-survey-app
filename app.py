import json
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Feruzaxon Journal Survey",
    page_icon="📘",
    layout="centered"
)

VERSION = "2.0"
TOPIC = "Academic Journal Keeping and Personal Insight Development Survey for University Students"

QUESTIONS = [
    {"category": "Journal Frequency", "question": "How often do you write about your academic experiences in a journal?"},
    {"category": "Reflection", "question": "How often do you reflect on what you learned during the day?"},
    {"category": "Reflection", "question": "How often do you record your thoughts about academic challenges?"},
    {"category": "Emotional Awareness", "question": "How often do you write about your feelings related to studying?"},
    {"category": "Reflection", "question": "How often do you review your journal entries to understand your progress?"},
    {"category": "Personal Insight", "question": "How often does journaling help you identify your academic strengths?"},
    {"category": "Personal Insight", "question": "How often does journaling help you notice your academic weaknesses?"},
    {"category": "Goal Setting", "question": "How often do you use journal writing to set personal academic goals?"},
    {"category": "Personal Insight", "question": "How often do you gain new personal insights while writing in your journal?"},
    {"category": "Emotional Awareness", "question": "How often does journaling help you understand your emotions better?"},
    {"category": "Improvement", "question": "How often do your journal entries help you improve your study habits?"},
    {"category": "Reflection", "question": "How often do you write honestly about your academic mistakes?"},
    {"category": "Improvement", "question": "How often do you connect your journal reflections to future improvement?"},
    {"category": "Emotional Awareness", "question": "How often does journaling help you manage academic stress?"},
    {"category": "Personal Development", "question": "How often do you feel that journal keeping is meaningful for your personal development?"}
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

CATEGORY_DESCRIPTIONS = {
    "Journal Frequency": "How regularly the student writes academic journal entries.",
    "Reflection": "How actively the student reflects on experiences, mistakes, and progress.",
    "Emotional Awareness": "How journaling supports emotional understanding and stress management.",
    "Personal Insight": "How journaling helps identify strengths, weaknesses, and deeper insights.",
    "Goal Setting": "How journaling contributes to academic planning and goal formation.",
    "Improvement": "How reflections are transformed into better study habits and future action.",
    "Personal Development": "How meaningful journaling feels for overall self-development."
}

st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 2.1rem;
    font-weight: 700;
    color: #1f3b73;
    margin-bottom: 0.1rem;
}
.sub-title {
    text-align: center;
    color: #4a4a4a;
    font-size: 1rem;
    margin-bottom: 1.5rem;
}
.info-box {
    background-color: #f3f7ff;
    padding: 16px;
    border-radius: 12px;
    border-left: 6px solid #4a76d1;
    margin-bottom: 1rem;
}
.result-box {
    background-color: #f8fbff;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #d7e3ff;
}
.small-note {
    color: #666666;
    font-size: 0.92rem;
}
</style>
""", unsafe_allow_html=True)


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
            "You demonstrate a highly consistent journaling habit and strong reflective ability. Continue using your journal to maintain progress, document learning, and support personal growth.",
        "Good reflective habit and useful personal insight":
            "You show a positive pattern of reflection and journal use. Try to deepen your entries by writing more specifically about emotions, lessons learned, and future plans.",
        "Moderate journaling and developing self-awareness":
            "You use journaling sometimes, but not regularly enough to gain its full benefit. More consistent writing may strengthen your insight and improve self-awareness.",
        "Limited journaling and weak insight development":
            "Your current journal practice appears limited. Start with short, simple entries after classes or study sessions and reflect on one challenge and one improvement point.",
        "Very low journaling engagement and minimal reflective insight":
            "You may benefit from starting an academic journal from the beginning. Even writing a few sentences each day about learning, feelings, and goals can gradually improve insight."
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
            "category": QUESTIONS[i - 1]["category"],
            "question_text": QUESTIONS[i - 1]["question"],
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


def build_category_dataframe(answers):
    category_scores = {}
    category_counts = {}

    for answer in answers:
        category = answer["category"]
        category_scores[category] = category_scores.get(category, 0) + answer["score"]
        category_counts[category] = category_counts.get(category, 0) + 1

    rows = []
    for category, total in category_scores.items():
        avg_score = round(total / category_counts[category], 2)
        rows.append({
            "Category": category,
            "Average Score": avg_score
        })

    return pd.DataFrame(rows).sort_values("Average Score", ascending=False)


def create_text_report(record):
    lines = [
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
        lines.append("")
        lines.append(f"Question {answer['question_number']}: {answer['question_text']}")
        lines.append(f"Category: {answer['category']}")
        lines.append(f"Chosen answer: {answer['selected_option_text']}")
        lines.append(f"Score: {answer['score']}")

    return "\n".join(lines)


with st.sidebar:
    st.header("Project Information")
    st.write("**Author:** Feruza Abdusattorova")
    st.write("**Course:** Fundamentals of Programming")
    st.write("**Version:** 2.0")
    st.divider()
    st.write("### Score interpretation")
    st.write("0–12 → Excellent journal practice")
    st.write("13–24 → Good reflective habit")
    st.write("25–36 → Moderate journaling")
    st.write("37–48 → Limited journaling")
    st.write("49–60 → Very low engagement")
    st.divider()
    st.write("### Category meaning")
    for category, description in CATEGORY_DESCRIPTIONS.items():
        st.write(f"**{category}:** {description}")

st.markdown('<div class="main-title">📘 Academic Journal Survey</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Academic Journal Keeping and Personal Insight Development Survey for University Students</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-box">
    This web application evaluates students' academic journal keeping habits and the level of personal insight gained from reflective writing.
    Please complete all fields and answer all 15 questions honestly. Lower scores indicate stronger journaling habits and deeper insight development.
    </div>
    """,
    unsafe_allow_html=True
)

progress_count = 0
for i in range(1, 16):
    if st.session_state.get(f"q_{i}") is not None:
        progress_count += 1

st.progress(progress_count / 15)
st.markdown(f"<div class='small-note'>Progress: {progress_count} of 15 questions answered</div>", unsafe_allow_html=True)

with st.expander("View scoring ranges and questionnaire purpose"):
    st.write("This questionnaire is designed for educational purposes to explore academic journaling habits, reflection, emotional awareness, and personal insight development.")
    for state, score_range in PSYCHOLOGICAL_STATES.items():
        st.write(f"**{state}**: {score_range[0]}–{score_range[1]}")

with st.form("survey_form"):
    st.subheader("Student Information")
    col1, col2 = st.columns(2)
    with col1:
        given_name = st.text_input("Given name")
    with col2:
        surname = st.text_input("Surname")

    col3, col4 = st.columns(2)
    with col3:
        dob = st.text_input("Date of birth (YYYY-MM-DD)")
    with col4:
        student_id = st.text_input("Student ID (digits only)")

    st.subheader("Survey Questions")
    selected_answers = []
    option_labels = list(OPTIONS.keys())

    for index, item in enumerate(QUESTIONS, start=1):
        answer = st.radio(
            f"Q{index}. {item['question']}",
            option_labels,
            index=None,
            key=f"q_{index}"
        )
        selected_answers.append(answer)

    submitted = st.form_submit_button("Submit Survey")

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
        errors.append("Please answer all 15 questions before submitting.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        record = build_result_record(given_name, surname, dob, student_id, selected_answers)
        category_df = build_category_dataframe(record["answers"])

        st.success("Survey submitted successfully.")
        st.divider()

        tab1, tab2, tab3 = st.tabs(["Result Summary", "Category Analysis", "Downloads"])

        with tab1:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.subheader("Survey Result")
            st.write(f"**Student:** {record['student']['given_name']} {record['student']['surname']}")
            st.write(f"**Total score:** {record['total_score']} / 60")
            st.write(f"**Result state:** {record['result_state']}")
            st.info(record["recommendation"])
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.subheader("Average score by category")
            st.caption("Higher average score means weaker performance in that area.")
            st.bar_chart(category_df.set_index("Category"))
            st.dataframe(category_df, use_container_width=True)

        with tab3:
            json_text = json.dumps(record, indent=4, ensure_ascii=False)
            txt_text = create_text_report(record)

            st.download_button(
                label="Download result as JSON",
                data=json_text,
                file_name=f"{student_id}_journal_survey_result.json",
                mime="application/json"
            )

            st.download_button(
                label="Download result as TXT",
                data=txt_text,
                file_name=f"{student_id}_journal_survey_result.txt",
                mime="text/plain"
            )

            preview = json_text[:1200] + ("\n..." if len(json_text) > 1200 else "")
            st.code(preview, language="json")
