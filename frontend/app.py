import streamlit as st
import requests
from datetime import datetime

# -------------------------------------------------
# FastAPI Backend URL
# -------------------------------------------------
API_URL = "http://127.0.0.1:8000"

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
            "content": (
                "Hello! 👋 Welcome to the Document RAG Chatbot.\n\n"
                "You can greet me anytime.\n"
                "Upload a PDF, DOCX or TXT file and ask questions about it."
            )
        }
    ]

if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

if "document_name" not in st.session_state:
    st.session_state.document_name = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:

    st.header("📄 Document RAG")

    # -----------------------------
    # Clear Chat
    # -----------------------------
    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! 👋 Welcome to the Document RAG Chatbot.\n\n"
                    "Upload a PDF, DOCX or TXT file and ask questions about it."
                )
            }
        ]

        st.session_state.chat_history = []

        st.rerun()

    st.divider()

    # -----------------------------
    # Upload Document
    # -----------------------------
    st.subheader("📄 Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF, TXT or DOCX file",
        type=["pdf", "txt", "docx"]
    )

    if st.button("Upload"):

        if uploaded_file is None:

            st.warning("Please select a document.")

        elif (
            st.session_state.document_name == uploaded_file.name
            and st.session_state.document_uploaded
        ):

            st.info("This document is already uploaded.")

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
                        timeout=60
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.success(data["message"])

                        st.session_state.document_uploaded = True
                        st.session_state.document_name = uploaded_file.name

                    else:

                        st.error(
                            response.json().get(
                                "detail",
                                "Upload failed."
                            )
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "❌ Cannot connect to the FastAPI backend."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "⌛ Upload timed out."
                    )

                except Exception as e:

                    st.error(str(e))

    # -----------------------------
    # Current Document
    # -----------------------------
    if st.session_state.document_uploaded:

        st.success(
            f"📄 Current Document\n\n"
            f"**{st.session_state.document_name}**"
        )

    else:

        st.info("No document uploaded.")

    st.divider()

    # -----------------------------
    # Chat History
    # -----------------------------
    st.subheader("💬 Chat History")

    if len(st.session_state.chat_history) == 0:

        st.write("No conversations yet.")

    else:

        for chat in reversed(st.session_state.chat_history):

            with st.expander(chat["time"]):

                st.markdown(
                    f"**👤 Question:**\n\n{chat['question']}"
                )

                st.markdown(
                    f"**🤖 Answer:**\n\n{chat['answer']}"
                )

# -------------------------------------------------
# Display Previous Messages
# -------------------------------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])
        # -------------------------------------------------
# Chat Input
# -------------------------------------------------
question = st.chat_input("💬 Type your message...")

# -------------------------------------------------
# Chat
# -------------------------------------------------
if question:

    # Display user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Assistant response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "question": question
                    },
                    timeout=60
                )

                if response.status_code == 200:

                    data = response.json()

                    answer = data["answer"]

                    # Optional: Show processing time if backend returns it
                    if "processing_time" in data:
                        st.caption(
                            f"⏱ Response generated in "
                            f"{data['processing_time']} seconds"
                        )

                else:

                    answer = response.json().get(
                        "detail",
                        "Unexpected server error."
                    )

            except requests.exceptions.ConnectionError:

                answer = (
                    "❌ Unable to connect to the FastAPI backend.\n\n"
                    "Make sure the backend server is running."
                )

            except requests.exceptions.Timeout:

                answer = "⌛ Request timed out."

            except Exception as e:

                answer = f"Unexpected Error:\n\n{str(e)}"

            st.markdown(answer)

    # Save assistant message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    # Save chat history
    st.session_state.chat_history.append(
        {
            "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "question": question,
            "answer": answer
        }
    )