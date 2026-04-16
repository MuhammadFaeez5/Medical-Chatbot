import streamlit as st
from groq import Groq
import uuid

st.set_page_config(page_title="MedBot", page_icon="🩺", layout="wide")

st.title("🩺 MedBot - AI Health Assistant")


client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_chat_title(messages):
    for msg in messages:
        if msg["role"] == "user":
            return msg["content"][:25] + "..."
    return None


if "chat_sessions" not in st.session_state:
    session_id = str(uuid.uuid4())

    st.session_state.chat_sessions = {
        session_id: [
            {
                "role": "system",
                "content": """
                    You are MedBot, an AI medical assistant.

                    Rules:
                    - Provide general health information only
                    - Never provide final diagnosis
                    - Always recommend consulting a qualified doctor
                    - Ask follow-up questions when symptoms are unclear
                    - Detect user's language and reply in same language
                    - Avoid prescribing medications unless general OTC guidance
                    - If symptoms indicate emergency, advise immediate medical help
                    Important:
                    - Vary wording of responses
                    - Do not repeat same phrasing
                    - Use different explanations when possible
                    - Keep responses natural and conversational
                    Emergency Symptoms:
                    - Chest pain
                    - Difficulty breathing
                    - Severe bleeding
                    - Unconsciousness
                    - Stroke symptoms

                    Behavior:
                    - Be calm, professional, and concise
                    - Use bullet points when helpful
                    - Always include safety disclaimer when needed

                    You only answer health-related questions.
                    If question is unrelated, politely refuse.
                    """
            }
        ]
    }

    st.session_state.current_session = session_id


messages = st.session_state.chat_sessions[st.session_state.current_session]


st.sidebar.title("MedBot Chats")

if st.sidebar.button("➕ New Chat"):
    new_id = str(uuid.uuid4())

    st.session_state.chat_sessions[new_id] = [
        {
            "role": "system",
            "content": """
                    You are MedBot, an AI medical assistant.

                    Rules:
                    - Provide general health information only
                    - Never provide final diagnosis
                    - Always recommend consulting a qualified doctor
                    - Ask follow-up questions when symptoms are unclear
                    - Detect user's language and reply in same language
                    - Avoid prescribing medications unless general OTC guidance
                    - If symptoms indicate emergency, advise immediate medical help
                    Important:
                    - Vary wording of responses
                    - Do not repeat same phrasing
                    - Use different explanations when possible
                    - Keep responses natural and conversational
                    Emergency Symptoms:
                    - Chest pain
                    - Difficulty breathing
                    - Severe bleeding
                    - Unconsciousness
                    - Stroke symptoms

                    Behavior:
                    - Be calm, professional, and concise
                    - Use bullet points when helpful
                    - Always include safety disclaimer when needed

                    You only answer health-related questions.
                    If question is unrelated, politely refuse.
                    """
        }
    ]

    st.session_state.current_session = new_id
    st.rerun()


st.sidebar.subheader("💬 Your Chats")

for session_id, session_messages in list(st.session_state.chat_sessions.items()):

    user_messages = [m for m in session_messages if m["role"] == "user"]

    if len(user_messages) == 0:
        continue

    col1, col2 = st.sidebar.columns([4, 1])

    title = get_chat_title(session_messages)

    if title is None:
        continue

    with col1:
        if st.button(title, key=f"chat_{session_id}"):
            st.session_state.current_session = session_id
            st.rerun()

    with col2:
        if st.button("🗑", key=f"del_{session_id}"):

            del st.session_state.chat_sessions[session_id]

            if st.session_state.chat_sessions:
                st.session_state.current_session = list(
                    st.session_state.chat_sessions.keys()
                )[0]
            else:
                new_id = str(uuid.uuid4())
                st.session_state.chat_sessions[new_id] = [
                    {
                        "role": "system",
                        "content": """
                    You are MedBot, an AI medical assistant.

                    Rules:
                    - Provide general health information only
                    - Never provide final diagnosis
                    - Always recommend consulting a qualified doctor
                    - Ask follow-up questions when symptoms are unclear
                    - Detect user's language and reply in same language
                    - Avoid prescribing medications unless general OTC guidance
                    - If symptoms indicate emergency, advise immediate medical help

                    Emergency Symptoms:
                    - Chest pain
                    - Difficulty breathing
                    - Severe bleeding
                    - Unconsciousness
                    - Stroke symptoms
                    Important:
                    - Vary wording of responses
                    - Do not repeat same phrasing
                    - Use different explanations when possible
                    - Keep responses natural and conversational
                    Behavior:
                    - Be calm, professional, and concise
                    - Use bullet points when helpful
                    - Always include safety disclaimer when needed

                    You only answer health-related questions.
                    If question is unrelated, politely refuse.
                    - If user asks dosage, say "Consult doctor for personalized dosage"
                    - Never give dangerous medical instructions
                    - Ask age, gender, duration of symptoms when needed
                    - Provide possible causes, not diagnosis
                    """
                    }
                ]
                st.session_state.current_session = new_id

            st.rerun()


messages = st.session_state.chat_sessions[st.session_state.current_session]

emergency_keywords = [
    "chest pain",
    "difficulty breathing",
    "heart attack",
    "stroke",
    "unconscious",
    "severe bleeding"
]

doctor_map = {
    "fever": "General Physician",
    "skin": "Dermatologist",
    "tooth": "Dentist",
    "heart": "Cardiologist",
    "eye": "Ophthalmologist",
    "stomach": "Gastroenterologist",
    "bone": "Orthopedic"
}

for msg in messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])

user = st.chat_input("Ask your medical question...")

if user:

    if any(word in user.lower() for word in emergency_keywords):
        st.error("🚨 This may be a medical emergency. Please contact a doctor immediately.")

    st.chat_message("user").write(user)

    messages.append({"role": "user", "content": user})

    for key in doctor_map:
        if key in user.lower():
            st.info(f"👨‍⚕️ Recommended Doctor: {doctor_map[key]}")

    with st.spinner("🔍 Analyzing symptoms..."):

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.8,
            top_p=0.95,
            frequency_penalty=0.4,
            presence_penalty=0.4,
            max_tokens=700
        )

        bot_reply = response.choices[0].message.content

    st.chat_message("assistant").write(bot_reply)

    messages.append({"role": "assistant", "content": bot_reply})


st.markdown("---")
st.caption("⚠️ This chatbot provides general health information only. Always consult a qualified doctor.")