import streamlit as st
import re
import random
import html

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Flashcard Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "flashcards": [],
    "current": 0,
    "show_answer": False,
    "status": {},
    "study_mode": "All Cards",
    "cards_to_generate": 15,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# FLASHCARD GENERATION
# ============================================================

def clean_sentence(sentence):
    sentence = re.sub(r"\s+", " ", sentence).strip()
    return sentence.strip(" -•\t")


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    sentences = [clean_sentence(p) for p in parts]

    return [
        s for s in sentences
        if len(s.split()) >= 4
    ]


def important_phrase(sentence):
    patterns = [
        r"^([A-Za-z][A-Za-z0-9\s\-]{2,50}?)\s+is\s+",
        r"^([A-Za-z][A-Za-z0-9\s\-]{2,50}?)\s+are\s+",
        r"^([A-Za-z][A-Za-z0-9\s\-]{2,50}?)\s+refers to\s+",
        r"^([A-Za-z][A-Za-z0-9\s\-]{2,50}?)\s+means\s+",
        r"^([A-Za-z][A-Za-z0-9\s\-]{2,50}?)\s+can be\s+",
    ]

    for pattern in patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)

        if match:
            return match.group(1).strip()

    words = re.findall(r"[A-Za-z][A-Za-z\-]*", sentence)

    if not words:
        return "this concept"

    capitalized = [
        word for word in words
        if word[0].isupper()
    ]

    if capitalized:
        return " ".join(capitalized[:3])

    return " ".join(words[:5])


def create_question(sentence, concept):
    lower = sentence.lower()

    if any(
        phrase in lower
        for phrase in [" is ", " are ", " refers to ", " means "]
    ):
        return f"What is {concept}?"

    if any(
        word in lower
        for word in ["function", "purpose", "used", "use"]
    ):
        return f"What is the purpose of {concept}?"

    if any(
        word in lower
        for word in ["advantage", "benefit", "importance"]
    ):
        return f"What is the importance of {concept}?"

    if any(
        word in lower
        for word in ["example", "examples"]
    ):
        return f"Can you give an example related to {concept}?"

    return f"Explain {concept}."


def generate_flashcards(text, limit=None):
    sentences = split_sentences(text)

    cards = []
    seen = set()

    for sentence in sentences:
        concept = important_phrase(sentence)
        question = create_question(sentence, concept)

        key = question.lower().strip()

        if key not in seen:
            seen.add(key)

            cards.append({
                "question": question,
                "answer": sentence,
                "concept": concept
            })

        if limit and len(cards) >= limit:
            break

    return cards


# ============================================================
# STUDY HELPERS
# ============================================================

def visible_cards():
    cards = st.session_state.flashcards
    mode = st.session_state.study_mode

    if mode == "Need Revision":
        return [
            i for i in range(len(cards))
            if st.session_state.status.get(i) == "Need Revision"
        ]

    if mode == "Known":
        return [
            i for i in range(len(cards))
            if st.session_state.status.get(i) == "Known"
        ]

    return list(range(len(cards)))


def reset_progress():
    st.session_state.status = {}
    st.session_state.current = 0
    st.session_state.show_answer = False


def escape_text(value):
    return html.escape(str(value))


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

    /* ---------- General ---------- */

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- Header ---------- */

    .hero {
        padding: 2.2rem 1rem 1.5rem 1rem;
        text-align: center;
    }

    .hero-icon {
        font-size: 3.2rem;
        margin-bottom: 0.4rem;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 850;
        letter-spacing: -1.5px;
        margin: 0;
    }

    .hero-subtitle {
        color: #6b7280;
        font-size: 1.08rem;
        margin-top: 0.7rem;
    }

    /* ---------- Feature cards ---------- */

    .feature-card {
        border: 1px solid rgba(120,120,120,0.18);
        border-radius: 18px;
        padding: 1.25rem;
        min-height: 130px;
        background: rgba(128,128,128,0.04);
    }

    .feature-icon {
        font-size: 1.7rem;
    }

    .feature-title {
        font-weight: 750;
        font-size: 1rem;
        margin-top: 0.45rem;
    }

    .feature-text {
        color: #6b7280;
        font-size: 0.88rem;
        margin-top: 0.25rem;
    }

    /* ---------- Section titles ---------- */

    .section-title {
        font-size: 1.45rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.25rem;
    }

    .section-description {
        color: #6b7280;
        margin-bottom: 1rem;
    }

    /* ---------- Flashcard ---------- */

    .flashcard {
        border: 1px solid rgba(120,120,120,0.22);
        border-radius: 26px;
        padding: 2.6rem;
        min-height: 350px;
        margin: 1rem 0;
        background: rgba(128,128,128,0.035);
        box-shadow: 0 12px 35px rgba(0,0,0,0.05);
    }

    .card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.6rem;
    }

    .question-label {
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #7c3aed;
    }

    .concept-pill {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        background: rgba(124,58,237,0.10);
        color: #7c3aed;
        font-weight: 700;
    }

    .question-text {
        font-size: 2rem;
        line-height: 1.3;
        font-weight: 800;
        margin: 1rem 0 2.2rem 0;
    }

    .think-box {
        border-radius: 15px;
        padding: 1rem 1.2rem;
        background: rgba(124,58,237,0.07);
        color: #6b7280;
        text-align: center;
    }

    .answer-label {
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #059669;
        margin-top: 1.5rem;
    }

    .answer-box {
        margin-top: 0.65rem;
        padding: 1.25rem;
        border-radius: 16px;
        background: rgba(5,150,105,0.08);
        line-height: 1.65;
        font-size: 1.05rem;
    }

    /* ---------- Stats ---------- */

    .stat-card {
        border: 1px solid rgba(120,120,120,0.18);
        border-radius: 17px;
        padding: 1rem;
        text-align: center;
        background: rgba(128,128,128,0.035);
    }

    .stat-number {
        font-size: 1.7rem;
        font-weight: 800;
    }

    .stat-label {
        color: #6b7280;
        font-size: 0.78rem;
        margin-top: 0.2rem;
    }

    /* ---------- Empty state ---------- */

    .empty-state {
        text-align: center;
        padding: 4rem 1rem;
        border: 1px dashed rgba(120,120,120,0.3);
        border-radius: 22px;
        margin-top: 1rem;
    }

    .empty-icon {
        font-size: 3rem;
    }

    .empty-title {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 0.7rem;
    }

    .empty-text {
        color: #6b7280;
        margin-top: 0.35rem;
    }

    /* ---------- Buttons ---------- */

    div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 2.7rem;
    }

    /* ---------- Sidebar ---------- */

    .sidebar-title {
        font-size: 1.15rem;
        font-weight: 800;
    }

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">⚙️ Study Settings</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.session_state.cards_to_generate = st.slider(
        "Number of flashcards",
        min_value=5,
        max_value=50,
        value=st.session_state.cards_to_generate,
        step=5
    )

    st.caption(
        "The generator will create up to this many cards "
        "from your study material."
    )

    st.divider()

    st.markdown("### 📚 Your Study Set")

    total_cards = len(st.session_state.flashcards)

    known_count = sum(
        1 for value in st.session_state.status.values()
        if value == "Known"
    )

    revision_count = sum(
        1 for value in st.session_state.status.values()
        if value == "Need Revision"
    )

    st.metric("Total cards", total_cards)
    st.metric("Known", known_count)
    st.metric("Need revision", revision_count)

    st.divider()

    if st.button(
        "🗑️ Reset Progress",
        use_container_width=True
    ):
        reset_progress()
        st.success("Progress reset.")
        st.rerun()


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
<div class="hero">
    <div class="hero-icon">📚</div>
    <div class="hero-title">Smart Flashcard Generator</div>
    <div class="hero-subtitle">
        Turn your study material into interactive flashcards
        and learn smarter, faster.
    </div>
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# FEATURE CARDS
# ============================================================

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Generate instantly</div>
            <div class="feature-text">
                Convert your notes into useful questions automatically.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with f2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Active recall</div>
            <div class="feature-text">
                Hide answers and test yourself before revealing them.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with f3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Track progress</div>
            <div class="feature-text">
                Mark cards as known or send difficult cards to revision.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# TABS
# ============================================================

tab_create, tab_study = st.tabs(
    [
        "✨ Create Flashcards",
        "🧠 Study & Self-Test"
    ]
)


# ============================================================
# CREATE TAB
# ============================================================

with tab_create:

    st.markdown(
        '<div class="section-title">Create your study set</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Paste your notes, definitions, or study material below.'
        '</div>',
        unsafe_allow_html=True
    )

    text = st.text_area(
        "Study material",
        height=280,
        placeholder=(
            "Example:\n\n"
            "Artificial Intelligence is the simulation of "
            "human intelligence by machines.\n\n"
            "Machine learning is a branch of AI that enables "
            "systems to learn from data.\n\n"
            "Neural networks are computing systems inspired "
            "by biological neural networks."
        ),
        label_visibility="collapsed"
    )

    char_count = len(text)

    st.caption(
        f"📝 {char_count:,} characters"
    )

    generate_col, clear_col = st.columns([4, 1])

    with generate_col:

        if st.button(
            "✨ Generate Flashcards",
            use_container_width=True,
            type="primary"
        ):

            if not text.strip():

                st.warning(
                    "Please enter some study material first."
                )

            else:

                cards = generate_flashcards(
                    text,
                    st.session_state.cards_to_generate
                )

                if not cards:

                    st.warning(
                        "Not enough detailed material was found. "
                        "Try adding longer explanations or definitions."
                    )

                else:

                    st.session_state.flashcards = cards
                    st.session_state.current = 0
                    st.session_state.show_answer = False
                    st.session_state.status = {}

                    st.success(
                        f"🎉 Generated {len(cards)} flashcards!"
                    )

                    st.rerun()

    with clear_col:

        if st.button(
            "Clear",
            use_container_width=True
        ):
            st.rerun()


    # --------------------------------------------------------
    # GENERATED PREVIEW
    # --------------------------------------------------------

    if st.session_state.flashcards:

        st.divider()

        st.markdown(
            '<div class="section-title">Your flashcards</div>',
            unsafe_allow_html=True
        )

        st.caption(
            f"{len(st.session_state.flashcards)} cards ready to study."
        )

        for number, card in enumerate(
            st.session_state.flashcards,
            start=1
        ):

            status = st.session_state.status.get(
                number - 1
            )

            if status == "Known":
                icon = "✅"
            elif status == "Need Revision":
                icon = "🔄"
            else:
                icon = "📝"

            with st.expander(
                f"{icon} Card {number} — {card['question']}"
            ):

                st.markdown(
                    f"**Answer:** {card['answer']}"
                )


# ============================================================
# STUDY TAB
# ============================================================

with tab_study:

    if not st.session_state.flashcards:

        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">🧠</div>
                <div class="empty-title">
                    Your study deck is empty
                </div>
                <div class="empty-text">
                    Go to "Create Flashcards" and generate your
                    first study set.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        cards = st.session_state.flashcards
        total = len(cards)

        known = sum(
            1 for value in st.session_state.status.values()
            if value == "Known"
        )

        revision = sum(
            1 for value in st.session_state.status.values()
            if value == "Need Revision"
        )

        completed = known + revision

        progress = (
            completed / total
            if total
            else 0
        )

        # ----------------------------------------------------
        # DASHBOARD STATS
        # ----------------------------------------------------

        s1, s2, s3, s4 = st.columns(4)

        with s1:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">TOTAL CARDS</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with s2:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">{known}</div>
                    <div class="stat-label">KNOWN</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with s3:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">{revision}</div>
                    <div class="stat-label">REVISION</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with s4:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">{round(progress * 100)}%</div>
                    <div class="stat-label">COMPLETED</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        st.progress(
            progress,
            text=f"Study progress — {round(progress * 100)}%"
        )

        # ----------------------------------------------------
        # FILTER
        # ----------------------------------------------------

        filter_col, info_col = st.columns([1, 2])

        with filter_col:

            st.session_state.study_mode = st.selectbox(
                "Study mode",
                [
                    "All Cards",
                    "Need Revision",
                    "Known"
                ],
                index=[
                    "All Cards",
                    "Need Revision",
                    "Known"
                ].index(
                    st.session_state.study_mode
                )
            )

        available = visible_cards()

        with info_col:

            if st.session_state.study_mode == "All Cards":
                st.caption(
                    f"Studying all {len(available)} cards."
                )

            elif st.session_state.study_mode == "Need Revision":
                st.caption(
                    f"Reviewing {len(available)} cards marked "
                    "for revision."
                )

            else:
                st.caption(
                    f"Reviewing your {len(available)} known cards."
                )

        # ----------------------------------------------------
        # EMPTY FILTER
        # ----------------------------------------------------

        if not available:

            st.info(
                "No cards are available in this filter yet."
            )

        else:

            # Make sure current card exists in filter
            if st.session_state.current not in available:

                st.session_state.current = available[0]
                st.session_state.show_answer = False

            current = st.session_state.current

            position = available.index(current) + 1

            card = cards[current]

            # ------------------------------------------------
            # CARD POSITION
            # ------------------------------------------------

            top_left, top_right = st.columns([3, 1])

            with top_left:
                st.caption(
                    f"FLASHCARD {position} OF {len(available)}"
                )

            with top_right:

                status = st.session_state.status.get(
                    current
                )

                if status == "Known":
                    st.success("✅ Known")

                elif status == "Need Revision":
                    st.warning("🔄 Revision")

            # ------------------------------------------------
            # FLASHCARD
            # ------------------------------------------------

            question = escape_text(card["question"])
            concept = escape_text(card["concept"])
            answer = escape_text(card["answer"])

            if st.session_state.show_answer:

                st.markdown(
                    f"""
                    <div class="flashcard">

                        <div class="card-top">
                            <div class="question-label">
                                QUESTION
                            </div>

                            <div class="concept-pill">
                                {concept}
                            </div>
                        </div>

                        <div class="question-text">
                            {question}
                        </div>

                        <div class="answer-label">
                            ANSWER
                        </div>

                        <div class="answer-box">
                            {answer}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="flashcard">

                        <div class="card-top">
                            <div class="question-label">
                                QUESTION
                            </div>

                            <div class="concept-pill">
                                {concept}
                            </div>
                        </div>

                        <div class="question-text">
                            {question}
                        </div>

                        <div class="think-box">
                            🧠 Think about your answer
                            before revealing it.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ------------------------------------------------
            # REVEAL
            # ------------------------------------------------

            reveal_text = (
                "🙈 Hide Answer"
                if st.session_state.show_answer
                else "👁️ Reveal Answer"
            )

            if st.button(
                reveal_text,
                use_container_width=True,
                type="primary"
            ):

                st.session_state.show_answer = (
                    not st.session_state.show_answer
                )

                st.rerun()

            # ------------------------------------------------
            # KNOW / REVISION
            # ------------------------------------------------

            if st.session_state.show_answer:

                st.write("")

                know_col, revision_col = st.columns(2)

                with know_col:

                    if st.button(
                        "✅ I Know This",
                        use_container_width=True
                    ):

                        st.session_state.status[
                            current
                        ] = "Known"

                        st.success(
                            "Great! Card marked as known."
                        )

                        st.rerun()

                with revision_col:

                    if st.button(
                        "🔄 Need Revision",
                        use_container_width=True
                    ):

                        st.session_state.status[
                            current
                        ] = "Need Revision"

                        st.warning(
                            "Added to your revision list."
                        )

                        st.rerun()

            st.divider()

            # ------------------------------------------------
            # NAVIGATION
            # ------------------------------------------------

            previous_col, random_col, next_col = st.columns(3)

            with previous_col:

                if st.button(
                    "⬅️ Previous",
                    use_container_width=True
                ):

                    idx = available.index(current)

                    st.session_state.current = (
                        available[
                            (idx - 1) % len(available)
                        ]
                    )

                    st.session_state.show_answer = False

                    st.rerun()

            with random_col:

                if st.button(
                    "🔀 Random Card",
                    use_container_width=True
                ):

                    if len(available) > 1:

                        choices = [
                            i for i in available
                            if i != current
                        ]

                        st.session_state.current = (
                            random.choice(choices)
                        )

                    st.session_state.show_answer = False

                    st.rerun()

            with next_col:

                if st.button(
                    "Next ➡️",
                    use_container_width=True
                ):

                    idx = available.index(current)

                    st.session_state.current = (
                        available[
                            (idx + 1) % len(available)
                        ]
                    )

                    st.session_state.show_answer = False

                    st.rerun()

        # ----------------------------------------------------
        # COMPLETION MESSAGE
        # ----------------------------------------------------

        if total > 0 and completed == total:

            st.divider()

            st.success(
                "🎉 You've reviewed every card in this study set!"
            )

            if known == total:

                st.balloons()

                st.markdown(
                    """
                    ### 🏆 Perfect!

                    Every flashcard is marked **Known**.
                    """
                )

            else:

                st.markdown(
                    f"""
                    ### 📚 Study session complete

                    You know **{known}** cards and have
                    **{revision}** cards to revise.
                    """
                )
