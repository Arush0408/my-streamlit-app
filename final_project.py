import streamlit as st
from google import genai
from google.genai import types

# 1. Page ki Setting (Sundar interface)
st.set_page_config(page_title="AI Forensic Hub", layout="wide")
st.title("⚖️ AI Forensic Hub: Fraud Detector")
st.write("Gemini 3.1 Flash-Lite ki 'Thinking' power se jhooth pakdiye.")

# 2. Sidebar mein API Key
api_key = st.sidebar.text_input("AIzaSyA4Ll9mA-wodm2MZv_8MWDo2NSk8gbBwi4", type="password")

# 3. Input Section
user_data = st.text_area("Yahan wo text ya logs paste karo jisme tumhe shak hai:", height=200)

if st.button("Start Deep Analysis"):
    if api_key and user_data:
        client = genai.Client(api_key=api_key)
        
        # Thinking Config: Yehi hai asli 'Dimaag'
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True, 
                thinking_level="high"
            ),
            system_instruction="Tum ek expert auditor ho. Text mein contradictions aur mathematical errors dhoondo."
        )

        with st.spinner("Gemini 'Think' kar raha hai..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite-preview",
                    config=config,
                    contents=[user_data]
                )

                # Output ko do hisson mein dikhana
                for part in response.candidates[0].content.parts:
                    if part.thought:
                        # AI ne kya socha (Backstage logic)
                        with st.expander("🧠 AI ki Soch (Internal Reasoning)"):
                            st.info(part.text)
                    elif part.text:
                        # AI ka final faisla
                        st.subheader("📊 Final Forensic Report")
                        st.success(part.text)
            
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("API Key aur Text dono bharna zaroori hai!")