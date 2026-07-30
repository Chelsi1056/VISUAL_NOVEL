# 🎮 Choose Your Own Adventure – AI Visual Novel Engine

An AI-powered interactive storytelling application built with **Streamlit** and **Google Gemini AI**. Create unique visual novels with AI-generated narratives, branching storylines, dynamic choices, and immersive text-to-speech narration.

---

## ✨ Features

- 📖 AI-generated interactive stories
- 🎭 Multiple story genres
- 🎨 Multiple AI art styles
- 🌳 Branching story paths with player choices
- 📂 JSON-based story generation and parsing
- 🖥️ Dynamic UI generation using Streamlit
- 🔊 Text-to-Speech narration
- 💾 Session state management for story progression
- ⚡ Fast and responsive interface

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Google Gemini API**
- **JSON**
- **gTTS (Google Text-to-Speech)**
- **Pillow**
- **Requests**

---

## 📂 Project Structure

```
Visual-Novel-Engine/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── LICENSE
│
└── assets/
    └── demo.mp4
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Visual-Novel-Engine.git
```

### 2. Navigate to the project

```bash
cd Visual-Novel-Engine
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API Key

Create:

```
.streamlit/secrets.toml
```

Add:

```toml
GEMINI_API_KEY="YOUR_API_KEY"
```

### 5. Run the application

```bash
streamlit run app.py
```

---

## 🎥 Demo

The project demo is available in:

```
assets/demo.mp4
```

*(You can also upload the video to YouTube or LinkedIn and add the link here.)*

---

## 📚 Engineering Concepts Implemented

This project demonstrates several concepts beyond basic Streamlit development:

- JSON Parsing
- Dynamic UI Generation
- AI-Powered Story Generation
- Text-to-Speech Integration
- Session State Management
- Prompt Engineering
- API Integration

---

## 🔮 Future Enhancements

- Save & Load Story Progress
- Character Memory
- Voice Selection
- Background Music
- Story Export (PDF/HTML)
- Multiplayer Story Mode

---

## 👩‍💻 Author

**Chelsi Aggarwal**

- GitHub: https://github.com/YOUR_USERNAME
- LinkedIn: https://www.linkedin.com/in/YOUR_LINKEDIN

---

## 📄 License

This project is licensed under the **MIT License**.
