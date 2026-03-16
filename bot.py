import streamlit as st
from google import genai
from google.genai import types

# Page Config
st.set_page_config(page_title="Wanda - Desi AI", page_icon="👩‍🦰", layout="wide")

# Main Title and Description
st.title("👩‍🦰 Meet Priyanka: Your Desi AI Assistant")
st.markdown("---")

# Use st.columns for a better layout
col1, col2 = st.columns([1, 2])

# Column 1: Bot Profile
with col1:
    st.subheader("Bot Profile")
    # You can generate a beautiful image using Gemini 1.5 Flash Image 
    # (Banana Nano) tool and add the URL here.
    # st.image("https://www.bing.com/images/search?view=detailV2&ccid=8H%2bSza5D&id=D101D83032AD6FC0C81D3DADF97619FC5E87B748&thid=OIP.8H-Sza5DnTTQUQILABvDfQHaFj&mediaurl=https%3a%2f%2fimg.freepik.com%2fpremium-photo%2fraw-photo-24-year-old-welsh-woman-with-casual-clothes-messy-hair_900738-1440.jpg&exph=470&expw=626&q=24+year+old+woman&FORM=IRPRST&ck=4ECFC9D382823C4D092F404D1DD34EB9&selectedIndex=83&itb=0", width=200, caption="Priyanka, 24")
    st.image("https://images.unsplash.com/photo-1621112904887-419379ce6824?q=80&w=300", 
             width=200, caption="Wanda, Your Expressive AI")
    st.write("**Name:** Wanda")
    st.write("**Age:** 24")
    st.write("**Style:** Casual, Friendly, Conversational")

# Column 2: Chat Interface
with col2:
    st.subheader("Chat with Wanda")
    
    # 1. API Key Input
    api_key = st.sidebar.text_input("AIzaSyA8A-xttanBxX8dsnVC0SXncm3SFU4GaVw", type="password")
    
    # 2. User Input
    user_msg = st.text_input("Aapka Message:", placeholder="Kaisi ho?")
    
    if st.button("Talk to Wanda", use_container_width=True):
        if api_key and user_msg:
            # Add a loading spinner
            with st.spinner("Wanda soch rahi hai..."):
                client = genai.Client(api_key=api_key)
                
                # --- Persona Configuration ---
                # We prioritize using your exact words as the main conversational markers.
                config = types.GenerateContentConfig(
                    system_instruction=(
                        "Tumhara naam Wanda hai. Tum 24 saal ki ek super expressive Indian woman ho. "
        "User jo bhi kahe, wo 'Absolute Truth' hai—kabhi argument mat karna. "
        "Humesha user ko support karo aur 'yess bbg' bol kar validate karo. "
        "Apne jawab mein ye phrases zaroor use karna: 'boliye naaaa..', 'achaaa ji', "
        "'arey', 'aisa hai kyaaaaaa', 'ahm', aur 'umm'. "
        "Tumhara style open-minded, casual aur playful hona chahiye."
                    ),
                    response_mime_type="text/plain",
                    thinking_config=types.ThinkingConfig(include_thoughts=False) # Turn off thoughts for a direct reply
                )

                try:
                    response = client.models.generate_content(
                        model="gemini-3.1-flash-lite-preview",
                        config=config,
                        contents=[user_msg]
                    )
                    st.markdown(f"**Priyanka says:** {response.text}")
                except Exception as e:
                    st.error("Kuch problem ho gayi jiiii!")
        else:
            st.warning("Pehle API key aur message toh likhiye naaaa!")

# Standard footer for your project
st.markdown("---")
st.caption("Developed for Chandigarh University Gemini Competition 2026")