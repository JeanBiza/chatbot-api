from fastapi import FastAPI
from pydantic import BaseModel
from bot.intent import IntentDetector
from bot.llm import LLMHandler
import database

app = FastAPI(title="Chatbot API", description="Technical support chatbot API")

intent_detector = IntentDetector()
llm_handler = LLMHandler()


@app.on_event("startup")
def startup():
    database.init_db()


class MessageRequest(BaseModel):
    session_id: str
    message: str


class MessageResponse(BaseModel):
    session_id: str
    message: str
    source: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=MessageResponse)
def chat(request: MessageRequest):
    session_id = request.session_id
    message = request.message

    history = database.get_history(session_id)

    faq_answer = intent_detector.match(message)
    if faq_answer:
        database.save_message(session_id, "user", message)
        database.save_message(session_id, "assistant", faq_answer)
        return MessageResponse(session_id=session_id, message=faq_answer, source="faq")

    llm_answer = llm_handler.chat(message, history)
    database.save_message(session_id, "user", message)
    database.save_message(session_id, "assistant", llm_answer)

    return MessageResponse(session_id=session_id, message=llm_answer, source="llm")


@app.get("/session/{session_id}")
def get_session(session_id: str):
    history = database.get_history(session_id)
    if not history:
        return {"session_id": session_id, "history": [], "message": "Session not found or empty."}
    return {"session_id": session_id, "history": history}


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    database.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.get("/sessions")
def list_sessions():
    sessions = database.get_all_sessions()
    return {"sessions": sessions}