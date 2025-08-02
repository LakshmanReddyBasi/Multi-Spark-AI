# Multi Spark AI ⚡

A multimodal AI studio that combines **chat, vision, image generation, and voice input** into one seamless interface.

Built with:
- 🌐 **Streamlit** – UI
- 🧠 **Google Gemini** – Text & Vision
- 🎨 **Replicate (SDXL)** – Text-to-Image
- 🎤 **st-audiorec** – Voice Input
- 🌙 Dark Mode, Session Persistence, Downloadable Outputs


## 🔧 Features

- 💬 Chat with AI (Gemini Pro)
- 🖼️ Analyze uploaded images
- 🎙️ Voice-to-text input
- 🖼️ Generate AI art from text (SDXL)
- 🌙 Dark/Light mode toggle
- 💾 Download images & export chat
- 🔐 Secure API key handling
- 🧠 Auto-image description
- 📋 Copy-to-clipboard support


## 🚀 Technologies Used

| Tech | Purpose |
|------|--------|
| [Streamlit](https://streamlit.io) | Beautiful, reactive UI |
| [Google Gemini](https://aistudio.google.com/) | Text & vision intelligence |
| [Replicate](https://replicate.com/) | Run SDXL for image generation |
| `st-audiorec` | Voice input in browser |
| `python-dotenv` | Secure API key management |
| `Pillow` | Image handling |
| `streamlit-copy-button` | Copy functionality |

---

2. Set Up Environment
👉 Edit .env and add your API keys:
GOOGLE_API_KEY=your_gemini_api_key_here
REPLICATE_API_TOKEN=r8_your_replicate_token_here

3. Install Dependencies
pip install -r requirements.txt

4. Launch the App
streamlit run app.py


## 🚀 Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/LakshmanReddyBasi/Multi-Spark-AI
   cd multi-spark-ai
