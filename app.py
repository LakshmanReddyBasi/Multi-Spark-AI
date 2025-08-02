from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
import replicate
from PIL import Image
import time
import base64
from io import BytesIO

# Optional: for copy button
try:
    from streamlit_copy_button import copy_button
except ImportError:
    pass

# Configure API keys
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Initialize models
vis_model = genai.GenerativeModel("gemini-pro-vision")
language_model = genai.GenerativeModel("gemini-pro")

# Set page config
st.set_page_config(
    page_title="Multi Spark AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =======================================================================================
# 🌙 Dark Mode Toggle
# =======================================================================================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

bg_color = "#0f172a" if st.session_state.dark_mode else "#f5f7fa"
text_color = "#e2e8f0" if st.session_state.dark_mode else "#1e2a38"
card_bg = "#1e293b" if st.session_state.dark_mode else "white"
accent = "#60a5fa"

# =======================================================================================
# 🔧 Custom CSS + Watermark
# =======================================================================================
st.markdown(f"""
    <style>
    .stApp {{
        background: {bg_color};
        color: {text_color};
        font-family: 'Segoe UI', sans-serif;
    }}
    .stChatMessage {{
        border-radius: 16px;
        padding: 12px 16px;
        margin-bottom: 10px;
        background: {card_bg};
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }}
    .stChatMessage[user] {{
        background-color: #1d4ed8;
        color: white;
    }}
    .stChatMessage[assistant] {{
        background-color: #0f766e;
        color: white;
    }}
    .stButton>button {{
        background: {accent};
        color: {'#0f172a' if st.session_state.dark_mode else 'white'};
        border-radius: 12px;
        height: 45px;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        border-radius: 10px;
        border: 1px solid #475569;
        background: {'#1e293b' if st.session_state.dark_mode else 'white'};
        color: {text_color};
    }}
    .streamlit-expanderHeader {{
        color: {accent};
        font-weight: 600;
    }}
    .watermark {{
        position: fixed;
        bottom: 10px;
        right: 15px;
        color: rgba(96, 165, 250, 0.5);
        font-size: 20px;
        font-weight: bold;
        pointer-events: none;
        z-index: 100;
        font-family: 'Arial', sans-serif;
    }}
    .stCodeBlock {{
        border-radius: 10px;
        background: #0f172a;
    }}
    .suggestions {{
        font-size: 14px;
        color: #94a3b8;
        margin: 10px 0;
        padding: 10px;
        background: {'#1e293b' if st.session_state.dark_mode else '#f1f5f9'};
        border-radius: 8px;
    }}
    </style>

    <div class="watermark">⚡ Multi Spark AI</div>
""", unsafe_allow_html=True)

# =======================================================================================
# Stream response
# =======================================================================================
def stream_data(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.04)

# =======================================================================================
# Voice Input
# =======================================================================================
try:
    import st_audiorec
except ImportError:
    pass

def audiorec_prompting():
    with st.sidebar:
        if st.checkbox("🎤 Speak to AI"):
            st.write("🎙️ Hold to record...")
            wav_audio_data = st_audiorec.st_audiorec()
            if wav_audio_data is not None:
                st.session_state.voice_input = True
                return "Voice input received. (Add Whisper API for transcription.)"
    return None

# =======================================================================================
# Image Download Link
# =======================================================================================
def get_image_download_link(img_url, filename="image.png"):
    try:
        import requests
        response = requests.get(img_url)
        img_data = response.content
        b64 = base64.b64encode(img_data).decode()
        href = f'<a href="data:image/png;base64,{b64}" download="{filename}">📥 Download Image</a>'
        return href
    except:
        return "<small>Download failed</small>"

# Initialize requests
if "requests" not in st.session_state:
    import requests
    st.session_state.requests = requests

# =======================================================================================
# Sidebar
# =======================================================================================
st.sidebar.markdown("<h2 style='text-align: center; color: #60a5fa;'>⚡ Multi Spark AI</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #94a3b8;'>Multimodal AI Studio</p>", unsafe_allow_html=True)
st.sidebar.divider()

mode = "🌙 Dark" if st.session_state.dark_mode else "☀️ Light"
if st.sidebar.button(mode):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

task = st.sidebar.radio(
    "**Choose Tool**",
    options=["💬 Chat & Vision", "🖼️ Text to Image"],
    index=0,
    label_visibility="collapsed"
)

st.sidebar.divider()

if st.sidebar.button("🆕 New Chat", use_container_width=True):
    st.session_state.messages = []
    st.session_state.generated_images = []
    st.rerun()

voice_prompt = audiorec_prompting()

# =======================================================================================
# Main: Chat & Vision
# =======================================================================================
if task == "💬 Chat & Vision":
    st.markdown("<h1 style='text-align: center; color: #60a5fa;'>🧠 AI Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Chat, analyze images, or speak your mind</p>", unsafe_allow_html=True)

    with st.expander("📎 Upload Image (Optional)", expanded=False):
        uploaded_file = st.file_uploader("Upload for analysis...", type=["jpg", "jpeg", "png"], key="img_up")
        image = Image.open(uploaded_file) if uploaded_file else None
        if image:
            st.image(image, caption="Uploaded Image", use_container_width=True)
            if st.button("🔍 Describe Image"):
                with st.spinner("Thinking..."):
                    resp = vis_model.generate_content(["Describe this image in detail.", image])
                    desc = resp.text if resp and resp.text else "No description."
                    st.session_state.messages.append({"role": "assistant", "content": f"**Description:** {desc}"})
                    st.markdown(f"> {desc}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            try:
                copy_button(message["content"], before_copy="📋 Copy", after_copy="✅ Copied")
            except:
                pass

    st.markdown('<div class="suggestions">Try: "Explain this image", "Write Python code", "Summarize"</div>', unsafe_allow_html=True)

    prompt = st.chat_input("Ask me anything...") or voice_prompt

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            try:
                copy_button(prompt, before_copy="📋 Copy", after_copy="✅ Copied")
            except:
                pass

        with st.spinner("🧠 Thinking..."):
            try:
                if image and prompt:
                    response = vis_model.generate_content([prompt, image])
                elif prompt:
                    response = language_model.generate_content(prompt)
                else:
                    st.warning("Enter text or upload image.")
                    response = None
            except Exception as e:
                st.error(f"❌ Error: {e}")
                response = None

        if response and response.text:
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"):
                if any(kw in prompt.lower() for kw in ["code", "python", "html", "css"]):
                    st.code(response.text)
                else:
                    st.write_stream(stream_data(response.text))
                try:
                    copy_button(response.text, before_copy="📋 Copy", after_copy="✅ Copied")
                except:
                    pass

    if st.session_state.messages:
        chat_text = "\n\n".join([f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages])
        b64 = base64.b64encode(chat_text.encode()).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="chat_history.txt">💾 Export Chat</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)

# =======================================================================================
# Text to Image
# =======================================================================================
elif task == "🖼️ Text to Image":
    st.markdown("<h1 style='text-align: center; color: #60a5fa;'>🖼️ AI Image Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Turn words into art</p>", unsafe_allow_html=True)

    REPLICATE_API_TOKEN = st.sidebar.text_input("🔐 Replicate API Token", type="password", placeholder="r8_...")
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

    if not REPLICATE_API_TOKEN or not REPLICATE_API_TOKEN.startswith("r8_"):
        st.markdown("<div style='text-align: center; color: #f87171;'>⚠️ Enter valid token in sidebar</div>", unsafe_allow_html=True)
    else:
        prompt = st.text_input(
            "📝 Prompt",
            value="A cybernetic owl reading in a neon library, cinematic, 4K",
            placeholder="Describe your dream image..."
        )

        with st.expander("⚙️ Settings", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                width = st.number_input("Width", 256, 2048, 1024, 64)
                num_outputs = st.slider("Images", 1, 4, 1)
            with col2:
                height = st.number_input("Height", 256, 2048, 1024, 64)
                scheduler = st.selectbox("Scheduler", ["K_EULER", "DPMSolverMultistep", "DDIM"])
            steps = st.slider("Denoising Steps", 1, 150, 50)
            strength = st.slider("Prompt Strength", 0.0, 1.0, 0.8)

        if st.button("🎨 Generate", use_container_width=True):
            with st.status("🎨 Generating...", expanded=True) as status:
                try:
                    output = replicate.run(
                        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                        input={
                            "prompt": prompt,
                            "width": width,
                            "height": height,
                            "num_outputs": num_outputs,
                            "scheduler": scheduler,
                            "num_inference_steps": steps,
                            "guidance_scale": 7.5,
                            "prompt_strength": strength,
                            "negative_prompt": "blurry, distorted, ugly",
                            "refine": "expert_ensemble_refiner",
                            "high_noise_frac": 0.8
                        }
                    )
                    if output:
                        status.update(label="✅ Done!", state="complete")
                        st.session_state.generated_images = output
                        st.markdown("### 🖼️ Generated Images")
                        cols = st.columns(len(output))
                        for idx, url in enumerate(output):
                            with cols[idx]:
                                st.image(url, caption=f"Image {idx+1}")
                                st.markdown(get_image_download_link(url, f"msai_img_{idx+1}.png"), unsafe_allow_html=True)
                    else:
                        st.error("No output.")
                except Exception as e:
                    st.error(f"Error: {e}")