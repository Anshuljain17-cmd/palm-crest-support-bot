import streamlit as st
from step3_chat import answer  # reuse the same bot logic from Step 3

st.set_page_config(page_title="Palm Crest Support Bot", page_icon="🏢")
st.title("🏢 Palm Crest Support Bot")
st.caption("Demo project: an AI assistant that answers only from the company FAQ "
           "and hands off to a human when unsure. (Fictional company and data.)")

# Keep the chat history between reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar with example questions and a reset button
with st.sidebar:
    st.header("Try asking")
    st.write("- Can I bring my dog?")
    st.write("- How much is the deposit for 90,000 AED rent?")
    st.write("- What are your office hours?")
    st.write("- Do you sell cars? (handoff test)")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

# Show previous messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Handle a new question
if question := st.chat_input("Ask a question about renting or buying..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the FAQ..."):
            reply, dist = answer(question)
        st.markdown(reply)
        st.caption(f"Match distance: {dist:.3f} (lower = closer match)")

    st.session_state.messages.append({"role": "assistant", "content": reply})
