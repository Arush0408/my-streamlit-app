import streamlit as st
from google import genai
from google.genai import types

# Page Config
st.set_page_config(page_title="Gemini Forensic Auditor", page_icon="🔍")
st.title("🔍 Gemini 3.1 Forensic Auditor")
st.caption("Using gemini-3.1-flash-lite-preview with High-Level Thinking")

# 1. Sidebar for API Key
api_key = st.sidebar.text_input("AIzaSyA4Ll9mA-wodm2MZv_8MWDo2NSk8gbBwi4", type="password")

# 2. Main Input Area
user_input = st.text_area("Paste Transcript or Logs to Audit", 
                          placeholder="e.g., Arush says he worked 500 hours...")

# 3. ONLY run if button is clicked AND api_key is provided
if st.button("Run Forensic Audit"):
    if not api_key:
        st.error("Please enter your API Key in the sidebar first!")
    elif not user_input:
        st.warning("Please paste some text to audit.")
    else:
        try:
            # Initialize client with the key from the text_input
            client = genai.Client(api_key=api_key)
            
            with st.spinner("Analyzing with High-Level Thinking..."):
                config = types.GenerateContentConfig(
                    system_instruction="You are a forensic data auditor. Output strictly in JSON format.",
                    response_mime_type="application/json",
                    thinking_config=types.ThinkingConfig(
                        include_thoughts=True, 
                        thinking_level="high"
                    )
                )

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite-preview",
                    config=config,
                    contents=[user_input]
                )

                # Separate Thoughts from Results
                for part in response.candidates[0].content.parts:
                    if part.thought:
                        with st.expander("🧠 View AI's Reasoning Process"):
                            st.write(part.text)
                    elif part.text:
                        st.subheader("📊 Audit Results")
                        st.json(part.text)
                        
        except Exception as e:
            st.error(f"API Error: {e}")