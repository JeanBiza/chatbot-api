from fastapi import FastAPI
from pydantic import BaseModel
from bot.intent import IntentDetector
from bot.llm import LLMHandler

app = FastAPI(title="Chatbot API", description="Technical support chatbot API")

intent_detector = IntentDetector()
llm_handler = LLMHandler()

sessions: dict[str, list] = {}


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

    if session_id not in sessions:
        sessions[session_id] = []

    faq_answer = intent_detector.match(message)
    if faq_answer:
        sessions[session_id].append({"role": "user", "content": message})
        sessions[session_id].append({"role": "assistant", "content": faq_answer})
        return MessageResponse(session_id=session_id, message=faq_answer, source="faq")
    
    history = sessions[session_id]
    llm_answer = llm_handler.chat(message, history)
    sessions[session_id].append({"role": "user", "content": message})
    sessions[session_id].append({"role": "assistant", "content": llm_answer})

    return MessageResponse(session_id=session_id, message=llm_answer, source="llm")


@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "cleared"}
    return {"status": "not found"}