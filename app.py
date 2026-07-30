"""
Novel Engine - AI Choose Your Own Adventure Visual Novel
Phases: Director's Cut UI, Structured JSON Engine, Dynamic UI Generation,
        Multi-Media Rendering & TTS, Graceful Failures
"""

import streamlit as st
from google import genai
from google.genai import types
import json
import requests
from gtts import gTTS
import time
import io

# -------------------------------------------------------------------
# PHASE 1: THE DIRECTOR'S CUT (UI & CONFIGURATION)
# -------------------------------------------------------------------

st.set_page_config(page_title="Novel Engine", page_icon="📖", layout="centered")


@st.cache_resource
def get_gemini_client():
    """Securely cache the Gemini client so it is not re-initialized on every rerun."""
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


st.sidebar.title("Story Settings")
genre = st.sidebar.selectbox(
    "Story Genre",
    ["Fantasy", "Sci-Fi", "Horror", "Mystery", "Post-Apocalyptic", "Cyberpunk"],
)
art_style = st.sidebar.selectbox(
    "Art Style",
    ["Digital Painting", "Anime", "Pixel Art", "Watercolor", "Noir Comic", "Photorealistic"],
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []          # list of {story_text, image_prompt, options, image_url}
if "gemini_chat" not in st.session_state:
    st.session_state.gemini_chat = None
if "current_scene" not in st.session_state:
    st.session_state.current_scene = None

SYSTEM_PROMPT = f"""You are the narrative engine for a {genre} choose-your-own-adventure
visual novel drawn in a {art_style} art style.

You must ALWAYS respond with STRICTLY VALID JSON and nothing else — no markdown fences,
no commentary before or after. The JSON object must contain exactly these keys:

{{
  "story_text": "A short, vivid narrative paragraph continuing the story.",
  "image_prompt": "A heavily detailed, comma-separated image generation prompt describing
                    the current scene, written for an AI image generator, including the
                    {art_style} style.",
  "options": ["Choice one", "Choice two", "Choice three"]
}}

The "options" list must contain 2 to 3 distinct, concrete actions the player can take next.
Do not include anything outside the JSON object.
"""

st.title("📖 Novel Engine")
st.caption(f"Genre: {genre} | Art Style: {art_style}")


# -------------------------------------------------------------------
# PHASE 2: THE STRUCTURED JSON ENGINE
# -------------------------------------------------------------------

def parse_ai_response(raw_text: str):
    """Parse the AI's raw string response into a Python dictionary. Handles stray
    markdown code fences and any stray text outside the JSON object."""
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    # If the model added any stray text before/after the JSON, isolate the
    # object by finding the first "{" and the matching last "}".
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def send_to_gemini(user_message: str):
    """Send a message to Gemini and return the parsed JSON scene dict, or None on failure."""
    client = get_gemini_client()

    if st.session_state.gemini_chat is None:
        st.session_state.gemini_chat = client.chats.create(
            model="gemini-flash-latest",
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )

    try:
        last_error = None
        response = None
        for attempt in range(3):
            try:
                response = st.session_state.gemini_chat.send_message(user_message)
                break
            except Exception as e:
                last_error = e
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    time.sleep(2 * (attempt + 1))  # 2s, 4s, 6s backoff
                    continue
                raise
        if response is None:
            raise last_error
        raw_text = response.text
    except Exception as e:
        st.toast("The story engine is busy. Please try again.", icon="⚠️")
        st.error(f"Gemini call failed: {e}")
        return None

    scene = parse_ai_response(raw_text)
    if scene is None:
        st.toast("The story engine returned an unreadable response. Please try again.", icon="⚠️")
        with st.expander("Debug: raw AI response (parsing failed)"):
            st.code(raw_text)
        return None

    return scene


# -------------------------------------------------------------------
# PHASE 4 (image half): FETCH IMAGE FROM POLLINATIONS
# -------------------------------------------------------------------

def fetch_image(image_prompt: str):
    """Download an image from the Pollinations API. Returns image bytes or None on failure."""
    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(image_prompt)}"
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return resp.content
    except Exception:
        st.toast("Image server is busy, skipping visual...", icon="🖼️")
        return None


# -------------------------------------------------------------------
# PHASE 4 (audio half): TTS NARRATION
# -------------------------------------------------------------------

def generate_narration(story_text: str):
    """Convert story_text to speech using gTTS. Returns audio bytes or None on failure."""
    try:
        tts = gTTS(text=story_text, lang="en")
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        st.toast("Narrator is unavailable, skipping audio...", icon="🔇")
        st.error(f"TTS generation failed: {e}")
        return None


# -------------------------------------------------------------------
# SCENE ADVANCEMENT
# -------------------------------------------------------------------

def advance_story(user_message: str) -> bool:
    scene = send_to_gemini(user_message)
    if scene is None:
        return False

    image_bytes = fetch_image(scene.get("image_prompt", ""))
    audio_bytes = generate_narration(scene.get("story_text", ""))

    st.session_state.current_scene = {
        "story_text": scene.get("story_text", ""),
        "options": scene.get("options", []),
        "image_bytes": image_bytes,
        "audio_bytes": audio_bytes,
    }
    st.session_state.chat_history.append(st.session_state.current_scene)
    return True


# -------------------------------------------------------------------
# INITIAL SCENE
# -------------------------------------------------------------------

if st.session_state.current_scene is None:
    if st.button("Begin Story"):
        if advance_story("Begin the story with an opening scene."):
            st.rerun()

# -------------------------------------------------------------------
# PHASE 4: RENDER CURRENT SCENE (persisted via session_state)
# -------------------------------------------------------------------

scene = st.session_state.current_scene
if scene is not None:
    st.write(scene["story_text"])

    if scene["image_bytes"]:
        st.image(scene["image_bytes"], use_column_width=True)

    if scene["audio_bytes"]:
        st.audio(scene["audio_bytes"], format="audio/mp3")

    st.divider()

    # -----------------------------------------------------------
    # PHASE 3: DYNAMIC UI GENERATION
    # -----------------------------------------------------------
    for i, option in enumerate(scene["options"]):
        if st.button(option, key=f"option_{len(st.session_state.chat_history)}_{i}"):
            if advance_story(option):
                st.rerun()