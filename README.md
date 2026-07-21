# Chatbot API

A local technical support chatbot API built with FastAPI, sentence-transformers and Ollama. Uses a hybrid approach — FAQ matching with embeddings for known questions, and a local LLM as fallback for everything else.

## Features

- **Embedding-based FAQ matching** — detects user intent using cosine similarity against a configurable FAQ dataset
- **LLM fallback** — routes unknown questions to a local Ollama model for natural language responses
- **Multi-session support** — each conversation is tracked independently by session ID
- **Persistent history** — conversation history stored in SQLite, survives server restarts
- **REST API** — clean endpoints consumable by any frontend, WhatsApp bot, Telegram bot, or web widget
- **Configurable FAQ** — edit `data/faq.json` to customize the bot for any domain

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com/) running locally with a model pulled (e.g. `qwen3:1.7b`)

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/JeanBiza/chatbot.git
cd chatbot
```

**2. Create a virtual environment and install dependencies**
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

**3. Make sure Ollama is running with a model**
```bash
ollama pull qwen3:1.7b
ollama serve
```

**4. Run the API**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Send a message and get a response |
| `GET` | `/session/{session_id}` | Get conversation history for a session |
| `DELETE` | `/session/{session_id}` | Clear a session's history |
| `GET` | `/sessions` | List all active session IDs |

### POST /chat

**Request:**
```json
{
    "session_id": "user123",
    "message": "How do I reset my password?"
}
```

**Response:**
```json
{
    "session_id": "user123",
    "message": "To reset your password, go to the login page and click 'Forgot Password'...",
    "source": "faq"
}
```

The `source` field indicates whether the response came from the FAQ (`"faq"`) or the LLM (`"llm"`).

## How it works

1. A message comes in via `POST /chat`
2. The intent detector encodes the message with `all-MiniLM-L6-v2` and computes cosine similarity against all FAQ questions
3. If similarity exceeds the threshold (0.75), the FAQ answer is returned immediately
4. Otherwise, the full conversation history is passed to the local Ollama model and the LLM response is returned
5. Both the user message and the response are saved to SQLite

## Customizing the FAQ

Edit `data/faq.json` to add, remove or modify questions and answers:

```json
{
    "faqs": [
        {
            "question": "How do I reset my password?",
            "answer": "Go to the login page and click Forgot Password..."
        }
    ]
}
```

The embeddings are computed at startup, so restart the server after editing the FAQ.

## Project structure

```
chatbot/
├── main.py              # FastAPI app and endpoints
├── database.py          # SQLite session persistence
├── bot/
│   ├── intent.py        # Embedding-based FAQ matcher
│   └── llm.py           # Ollama LLM handler
├── data/
│   └── faq.json         # Configurable FAQ dataset
└── requirements.txt
```

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) — REST API framework
- [sentence-transformers](https://www.sbert.net/) — embedding model for intent detection
- [Ollama](https://ollama.com/) — local LLM inference
- [scikit-learn](https://scikit-learn.org/) — cosine similarity
- SQLite — conversation history persistence