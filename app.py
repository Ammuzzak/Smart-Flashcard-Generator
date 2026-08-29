import streamlit as st
import re
import random

st.set_page_config(
    page_title="Smart Flashcard Generator",
    page_icon="📚",
    layout="wide"
)

# -----------------------------
# Session state
# -----------------------------
defaults = {
    "flashcards": [],
    "current": 0,
    "show_answer": False,
    "status": {},
    "study_mode": "All Cards",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------
# Flashcard generation logic
# -----------------------------
def clean_sentence(sentence):
    sentence = re.sub(r"\s+", " ", sentence).strip()
    return sentence.strip(" -•\t")


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    sentences = [clean_sentence(p) for p in parts]
    return [s for s in sentences if len(s.split()) >= 4]


def important_phrase(sentence):
    # Looks for common definition patterns first
    patterns = [
        r"^([A-Za-z][A-Za-z0-9\s\-]{2,50}?)\s+is\s+",
        r"^([A-Za-z][A-Za-z0-9\s\-]{2,50}?)\s+are\s+",
        r"^([A-Za-z][A-Za-z0-9\s\-]{2,50}?)\s+refers to\s+",
        r"^([A-Za-z][A-Za-z0-9\s\-]{2,50}?)\s+means\s+",
    ]
    for pattern in patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    words = re.findall(r"[A-Za-z][A-Za-z\-]*", sentence)
    if not words:
        return "this concept"

    # Prefer capitalized words or the first meaningful words
    capitalized = [w for w in words if w[0].isupper()]
    if capitalized:
        return " ".join(capitalized[:3])

    return " ".join(words[:5])


def create_question(sentence, concept):
    lower = sentence.lower()

    if " is " in lower or " are " in lower or " refers to " in lower or " means " in lower:
        return f"What is {concept}?"

    if any(word in lower for word in ["function", "purpose", "used", "use"]):
        return f"What is the purpose of {concept}?"

    if any(word in lower for word in ["advantage", "benefit", "importance"]):
        return f"What is the importance of {concept}?"

    return f"Explain {concept}."


def generate_flashcards(text):
    sentences = split_sentences(text)
    cards = []
    seen = set()

    for sentence in sentences:
        concept = important_phrase(sentence)
        question = create_question(sentence, concept)
        key = question.lower()

        if key not in seen:
            seen.add(key)
            cards.append({
                "question": question,
                "answer": sentence
            })

    return cards


def visible_cards():
    cards = st.session_state.flashcards
    mode = st.session_state.study_mode

    if mode == "Need Revision":
        return [i for i in range(len(cards))
                if st.session_state.status.get(i) == "Need Revision"]
    if mode == "Known":
        return [i for i in range(len(cards))
                if st.session_state.status.get(i) == "Known"]
    return list(range(len(cards)))


# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .flashcard {
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(120,120,120,0.25);
        min-height: 300px;
        margin: 1rem 0;
    }
    .question-label {
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 1px;
        color: #7c3aed;
    }
    .question-text {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 1rem 0 2rem 0;
    }
    .answer-box {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(124,58,237,0.08);
        font-size: 1.05rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="main-title">📚 Smart Flashcard Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Turn your study material into interactive flashcards and revise smarter.</div>',
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["📝 Create Flashcards", "🧠 Study & Self-Test"])

# -----------------------------
# Create flashcards
# -----------------------------
with tab1:
    st.subheader("Paste Your Study Material")

    text = st.text_area(
        "Enter notes, definitions, paragraphs, or study material:",
        height=250,
        placeholder="Example: Artificial Intelligence is the simulation of human intelligence by machines. Machine learning is a branch of AI that enables systems to learn from data..."
    )

    if st.button("✨ Generate Flashcards", use_container_width=True):
        if not text.strip():
            st.warning("Please enter some study material first.")
        else:
            cards = generate_flashcards(text)

            if not cards:
                st.warning("Please enter more detailed study material so flashcards can be generated.")
            else:
                st.session_state.flashcards = cards
                st.session_state.current = 0
                st.session_state.show_answer = False
                st.session_state.status = {}
                st.success(f"Successfully generated {len(cards)} flashcards! 🎉")

    if st.session_state.flashcards:
        st.subheader("Generated Flashcards")
        for number, card in enumerate(st.session_state.flashcards, start=1):
            with st.expander(f"Card {number}: {card['question']}"):
                st.write("**Answer:**", card["answer"])

# -----------------------------
# Study mode
# -----------------------------
with tab2:
    if not st.session_state.flashcards:
        st.info("👈 First create flashcards using the Create Flashcards tab.")
    else:
        cards = st.session_state.flashcards
        total = len(cards)
        known = sum(1 for v in st.session_state.status.values() if v == "Known")
        revision = sum(1 for v in st.session_state.status.values() if v == "Need Revision")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Cards", total)
        c2.metric("Known", known)
        c3.metric("Need Revision", revision)
        c4.metric("Progress", f"{round(((known + revision) / total) * 100)}%")

        st.progress((known + revision) / total)

        st.session_state.study_mode = st.selectbox(
            "Revision Mode",
            ["All Cards", "Need Revision", "Known"],
            index=["All Cards", "Need Revision", "Known"].index(st.session_state.study_mode)
        )

        available = visible_cards()

        if not available:
            st.info("No flashcards are available in this revision filter yet.")
        else:
            # Keep current card valid for selected filter
            if st.session_state.current not in available:
                st.session_state.current = available[0]
                st.session_state.show_answer = False

            current = st.session_state.current
            position = available.index(current) + 1
            card = cards[current]

            st.caption(f"Card {position} of {len(available)}")

            st.markdown('<div class="flashcard">', unsafe_allow_html=True)
            st.markdown('<div class="question-label">QUESTION</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="question-text">{card["question"]}</div>',
                unsafe_allow_html=True
            )

            if st.session_state.show_answer:
                st.markdown('<div class="question-label">ANSWER</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="answer-box">{card["answer"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.info("🧠 Think of your answer first, then reveal it when ready.")

            st.markdown('</div>', unsafe_allow_html=True)

            if st.button(
                "👁️ Hide Answer" if st.session_state.show_answer else "👁️ Show Answer",
                use_container_width=True
            ):
                st.session_state.show_answer = not st.session_state.show_answer
                st.rerun()

            if st.session_state.show_answer:
                a, b = st.columns(2)

                if a.button("✅ I Know This", use_container_width=True):
                    st.session_state.status[current] = "Known"
                    st.success("Marked as Known! 🎉")

                if b.button("🔄 Need Revision", use_container_width=True):
                    st.session_state.status[current] = "Need Revision"
                    st.warning("Marked for revision. You can practice it again!")

            st.divider()

            left, middle, right = st.columns([1, 2, 1])

            if left.button("⬅️ Previous", use_container_width=True):
                idx = available.index(current)
                st.session_state.current = available[(idx - 1) % len(available)]
                st.session_state.show_answer = False
                st.rerun()

            if middle.button("🔀 Random Card", use_container_width=True):
                st.session_state.current = random.choice(available)
                st.session_state.show_answer = False
                st.rerun()

            if right.button("Next ➡️", use_container_width=True):
                idx = available.index(current)
                st.session_state.current = available[(idx + 1) % len(available)]
                st.session_state.show_answer = False
                st.rerun()

        st.divider()

        if st.button("🗑️ Reset All Progress"):
            st.session_state.status = {}
            st.session_state.current = 0
            st.session_state.show_answer = False
            st.success("Progress has been reset.")
