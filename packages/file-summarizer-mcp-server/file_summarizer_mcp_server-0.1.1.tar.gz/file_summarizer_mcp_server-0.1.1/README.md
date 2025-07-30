# 📄 File Summarizer MCP Server

A fully offline, multi-modal file summarization server built with FastMCP. Supports text, documents, audio, and video files with language detection, translation, and speech-to-text capabilities.

## 🚀 Features

- 📂 **Reads multiple file types** — PDF, DOCX, TXT, audio (MP3, WAV), video (MP4, MOV) via Apache Tika & Whisper.
- 🧠 **Summarizes file content or raw input text** automatically.
- 🌐 **Multi-language support** — detects input language, translates to English if needed, or keeps summary in original language.
- 🎙 **Speech-to-text transcription** — audio/video files transcribed via Whisper before summarization.
- ⚙️ **Simple async MCP tools** — easy to extend and integrate with any MCP client.
- 🔒 Fully offline capable — no need for external LLM APIs.
- 🐍 Built with Python 3.12, FastMCP server framework, Apache Tika, Whisper, LangDetect, and Deep Translator.

## 🛠 Installation

1️⃣ Clone the repo:

```bash
git clone https://github.com/Muskan244/File_Summarizer_MCP_Server.git
cd File_Summarizer_MCP_Server
```

2️⃣ Setup virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

3️⃣ Install dependencies:

```bash
pip install -r requirements.txt
# Whisper requires ffmpeg installed system-wide
brew install ffmpeg  # (Mac)
```

## 🔧 Usage

Start the MCP server:

```bash
uv run file_summarizer.py
```

It exposes the following tools:

- `read_file(file_path)`
- `summarize_file(file_path)`
- `summarize_text(text)`
- `detect_language(text)`
- `translate_text(text)`
- `transcribe_file(file_path)`

You can invoke these via any MCP-compliant client (Claude Desktop, Open Interpreter, etc.).
