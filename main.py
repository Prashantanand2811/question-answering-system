# import os
# from fastapi import FastAPI
# from pydantic import BaseModel
# from .client import get_messages, known_names
# from .nlu import extract_member_name, detect_intent
# from .retrieve import topk_member_messages
# from .extract import extract_answer

# USE_LLM = os.getenv("USE_LLM", "false").lower() in ("1","true","yes")
# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")  # or "mistral", "phi3"

# app = FastAPI(title="Member QA (Grounded)")

# class AskIn(BaseModel):
#     question: str

# class AskOut(BaseModel):
#     answer: str

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/ask", response_model=AskOut)
# def ask(body: AskIn):
#     question = body.question.strip()
#     messages = get_messages()
#     names = known_names()

#     member = extract_member_name(question, names)
#     if not member:
#         return {"answer": "I couldn’t find any messages for that member."}

#     cands = topk_member_messages(question, messages, member, k=8)
#     if not cands:
#         return {"answer": "I couldn’t find any messages for that member."}

#     intent = detect_intent(question)

#     # 1) Fast deterministic extraction first
#     ans = extract_answer(question, intent, cands)

#     # 2) Optional LLM fallback (grounded RAG via Ollama)
#     if not ans and USE_LLM:
#         from .llm import ollama_answer
#         ans = ollama_answer(question, member, cands, model=OLLAMA_MODEL)

#     if not ans:
#         ans = "I can’t answer from the available messages."
#     return {"answer": ans}

# app/main.py
import os
from fastapi import FastAPI
from pydantic import BaseModel

from .client import get_messages, known_names
from .nlu import extract_member_name, detect_intent
from .retrieve import topk_member_messages
from .extract import extract_answer

USE_LLM = os.getenv("USE_LLM", "false").lower() in ("1", "true", "yes")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

app = FastAPI(title="Member QA (Rules + LLM)")

class AskIn(BaseModel):
    question: str

class AskOut(BaseModel):
    answer: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask", response_model=AskOut)
def ask(body: AskIn):
    question = body.question.strip()
    messages = get_messages()
    names = known_names()

    member = extract_member_name(question, names)
    if not member:
        return {"answer": "I couldn’t find any messages for that member."}

    cands = topk_member_messages(question, messages, member, k=8)
    if not cands:
        return {"answer": "I couldn’t find any messages for that member."}

    intent = detect_intent(question)

    # 1) Try rule-based extraction first (fast + precise)
    ans = extract_answer(question, intent, cands)

    # 2) LLM fallback or enhancement
    if USE_LLM:
        # For WHAT / OTHER, or if rules failed, let LLM refine/answer
        if intent in ("WHAT", "OTHER") or not ans:
            from .llm import ollama_answer
            llm_ans = ollama_answer(question, member, cands, model=OLLAMA_MODEL, intent=intent)
            if llm_ans:
                ans = llm_ans

    if not ans:
        ans = "I can’t answer from the available messages."

    return {"answer": ans}
