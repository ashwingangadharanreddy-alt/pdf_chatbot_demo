import streamlit as st
import requests
import os
from datetime import datetime

# -------------------------------------------------
# FastAPI Backend URL (use BACKEND_URL env var in Render)
# -------------------------------------------------
API_URL = os.getenv("BACKEND_URL") or "http://127.0.0.1:8000"

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Document RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Document RAG Chatbot")

# -------------------------------------------------
# Session State
# -------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content":
                "Hello! 👋 Welcome to the Document RAG Chatbot.\n\n"
                "Upload a PDF, DOCX or TXT document and ask me anything about it."
        }
    ]

if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

if "document_name" not in st.session_state:
    st.session_state.document_name = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# NEW
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

# NEW
if "selected_question" not in st.session_state:
    st.session_state.selected_question = None

# NEW
if "processing_time" not in st.session_state:
    st.session_state.processing_time = None
# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:

    st.header("📄 Document RAG")

    # ----------------------------------
    # Clear Chat
    # ----------------------------------
    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content":
                    "Hello! 👋 Welcome to the Document RAG Chatbot.\n\n"
                    "Upload a PDF, DOCX or TXT file and ask me questions."
            }
        ]

        st.session_state.chat_history = []
        st.session_state.suggestions = []
        st.session_state.selected_question = None
        st.session_state.processing_time = None

        st.rerun()

    st.divider()

    # ----------------------------------
    # Upload Document
    # ----------------------------------
    st.subheader("📄 Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF, DOCX or TXT file",
        type=["pdf", "txt", "docx"]
    )

    if st.button("Upload"):

        if uploaded_file is None:

            st.warning("Please select a document.")

        elif (
            st.session_state.document_uploaded
            and
            uploaded_file.name == st.session_state.document_name
        ):

            st.info("This document has already been uploaded.")

        else:

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            with st.spinner("Uploading document..."):

                try:

                    response = requests.post(
                        f"{API_URL}/upload",
                        files=files,
                        timeout=120
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.success(data["message"])

                        st.session_state.document_uploaded = True
                        st.session_state.document_name = uploaded_file.name

                        st.session_state.suggestions = []

                    else:

                        st.error(
                            response.json().get(
                                "detail",
                                "Upload failed."
                            )
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to FastAPI."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "Upload timed out."
                    )

                except Exception as e:

                    st.error(str(e))

    st.divider()

    # ----------------------------------
    # Current Document
    # ----------------------------------
    st.subheader("📄 Current Document")

    if st.session_state.document_uploaded:

        st.success(
            st.session_state.document_name
        )

    else:

        st.info("No document uploaded.")

    st.divider()

    # ----------------------------------
    # Chat History
    # ----------------------------------
    st.subheader("💬 Chat History")

    if len(st.session_state.chat_history) == 0:

        st.write("No conversations yet.")

    else:

        for chat in reversed(
            st.session_state.chat_history
        ):

            with st.expander(chat["time"]):

                st.markdown(
                    f"**👤 Question**\n\n{chat['question']}"
                )

                st.markdown(
                    f"**🤖 Answer**\n\n{chat['answer']}"
                )
# -------------------------------------------------
# Display Previous Messages
# -------------------------------------------------

for index, message in enumerate(st.session_state.messages):

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # ------------------------------------------
        # Display Suggestions Below Assistant Message
        # ------------------------------------------
        if (
            message["role"] == "assistant"
            and "suggestions" in message
            and len(message["suggestions"]) > 0
        ):

            st.markdown("### 💡 Related Questions")

            for i, suggestion in enumerate(message["suggestions"]):

                if st.button(
                    suggestion,
                    key=f"suggestion_{index}_{i}"
                ):

                    st.session_state.selected_question = suggestion
                    st.rerun()
# -------------------------------------------------
# Chat Input
# -------------------------------------------------

user_input = st.chat_input("💬 Type your message...")

# If a suggestion button was clicked,
# use that as the next question.
if st.session_state.selected_question:

    question = st.session_state.selected_question

    st.session_state.selected_question = None

else:

    question = user_input
# -------------------------------------------------
# Chat
# -------------------------------------------------

if question:

    # --------------------------------------------
    # User Message
    # --------------------------------------------
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # --------------------------------------------
    # Assistant Message
    # --------------------------------------------
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "question": question
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    data = response.json()

                    answer = data.get(
                        "answer",
                        "No answer returned."
                    )

                    suggestions = data.get(
                        "suggestions",
                        []
                    )

                    processing_time = data.get(
                        "processing_time",
                        None
                    )

                else:

                    answer = response.json().get(
                        "detail",
                        "Unexpected server error."
                    )

                    suggestions = []

                    processing_time = None

            except requests.exceptions.ConnectionError:

                answer = (
                    "❌ Unable to connect to FastAPI backend."
                )

                suggestions = []

                processing_time = None

            except requests.exceptions.Timeout:

                answer = "⌛ Request timed out."

                suggestions = []

                processing_time = None

            except Exception as e:

                answer = str(e)

                suggestions = []

                processing_time = None

            # ------------------------------------
            # Show Answer
            # ------------------------------------
            st.markdown(answer)

            # ------------------------------------
            # Response Time
            # ------------------------------------
            if processing_time is not None:

                st.caption(
                    f"⏱ Generated in {processing_time} sec"
                )

            # ------------------------------------
            # Suggested Questions
            # ------------------------------------
            if suggestions:

                st.markdown("### 💡 Related Questions")

                for i, suggestion in enumerate(suggestions):

                    if st.button(
                        suggestion,
                        key=f"new_{len(st.session_state.messages)}_{i}"
                    ):

                        st.session_state.selected_question = suggestion
                        st.rerun()

    # --------------------------------------------
    # Save Assistant Message
    # --------------------------------------------
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "suggestions": suggestions
        }
    )

    # --------------------------------------------
    # Save Chat History
    # --------------------------------------------
    st.session_state.chat_history.append(
        {
            "time": datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
            "question": question,
            "answer": answer
        }
    )