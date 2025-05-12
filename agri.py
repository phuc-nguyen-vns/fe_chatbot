import streamlit as st
import requests
import sys, os, json
from pathlib import Path

# --- Config ---
sys.path.append(Path(os.getcwd(), "FE_chatbot").as_posix())
from app_config import app_config

base_url = app_config.base_url
# base_url = "http://localhost:8000"
ANSWER_API = f"{base_url}/v2/demo/agriculture"
SUGGEST_API = f"{base_url}/v1/chat/next_question"

# --- Initialize session state ---
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []  # List[Dict: role/content/suggestions/metadata]
if "show_metadata" not in st.session_state:
    st.session_state.show_metadata = False  # Toggle state for metadata display

st.title("🌾 Agriculture Chat Assistant")

# --- Display Chat History ---
for msg in st.session_state.chat_log:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            # Show sources if available
            if "metadata" in msg and msg["metadata"].get("answer_source"):
                st.markdown("📚 **Sources:**")
                for src in msg["metadata"]["answer_source"]:
                    st.markdown(f"- 📄 *{src['filename']}* – Page {src['page']}, Chunk {src['chunk']}")
            if msg.get("suggestions"):
                st.markdown("💡 **Suggested next questions:**")
                for q in msg["suggestions"]:
                    st.markdown(f"- {q}")

# --- Input Box ---
query = st.chat_input("Ask a question about agriculture...")

if query:
    st.session_state.history.append(query)
    st.session_state.chat_log.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 1. Get Answer
    try:
        answer_res = requests.post(ANSWER_API, json={"query": query, "history": st.session_state.history})
        answer_res.raise_for_status()
        response_json = answer_res.json()
        answer = response_json.get("answer", "❌ No answer provided.").replace("\\n", "\n")
        metadata = response_json.get("metadata", {})
    except Exception as e:
        answer = f"❌ Error: {e}"
        metadata = {}

    # 2. Get Suggestions
    suggestions = []
    try:
        suggest_payload = {
            "query": query,
            "search_type": "hybrid",
            "semantic_ratio": 0.5,
            "embedder": "embedder",
            "top_k": 3,
            "index": "agri_chatbot_v2",
            "history": st.session_state.history
        }
        suggest_res = requests.post(SUGGEST_API, json=suggest_payload)
        suggest_res.raise_for_status()
        suggestions = json.loads(suggest_res.json()).get("suggestions", [])
    except Exception:
        suggestions = []

    # 3. Display Assistant Reply + Metadata + Suggestions
    with st.chat_message("assistant"):
        st.markdown(answer)
        if metadata.get("answer_source"):
            st.markdown("📚 **Sources:**")
            for src in metadata["answer_source"]:
                st.markdown(f"- 📄 *{src['filename']}* – Page {src['page']}, Chunk {src['chunk']}")
        if suggestions:
            st.markdown("💡 **Suggested next questions:**")
            for s in suggestions:
                st.markdown(f"- {s}")

    # 4. Save to Chat Log
    st.session_state.chat_log.append({
        "role": "assistant",
        "content": answer,
        "suggestions": suggestions,
        "metadata": metadata
    })

# --- Toggleable Metadata Button ---
if st.button("📖 Show All Metadata"):
    st.session_state.show_metadata = not st.session_state.show_metadata  # Toggle show/hide

if st.session_state.show_metadata:
    st.markdown("### 📖 **Full Metadata Across Conversation**")
    for idx, msg in enumerate(st.session_state.chat_log[-1:]):
        metadata = msg.get("metadata")
        st.markdown(f"#### Metadata:")
        if metadata:
            # Pretty print metadata JSON
            st.json(metadata)
        else:
            st.markdown("- 📄 No metadata available for this response.")


