# import json, re, subprocess

# SYSTEM = (
#     'You are a data-grounded assistant. Use ONLY the provided messages to answer.\n'
#     'If unsupported, reply exactly: {"answer":"I can’t answer from the available messages."}\n'
#     'Rules:\n'
#     '- For date/time questions, copy the date/time exactly from a message.\n'
#     '- For counts, return digits only (e.g., "3").\n'
#     '- For favorites, return a comma-separated list copied from the messages.\n'
#     '- Output strict JSON: {"answer":"..."}'
# )

# def build_prompt(question: str, member: str, snippets: list[dict]) -> str:
#     rows = [f"Question: {question}", f"Member: {member}", "\nMessages (newest first):"]
#     for i, m in enumerate(snippets[:8], 1):
#         txt = m["message"].strip().replace("\n"," ")
#         if len(txt) > 400: txt = txt[:397] + "..."
#         rows.append(f"[{i}] {txt}")
#     rows.append('\nReturn JSON: {"answer":"..."}')
#     return "\n".join(rows)

# def ollama_answer(question: str, member: str, snippets: list[dict], model="llama3") -> str:
#     prompt = f"{SYSTEM}\n\n{build_prompt(question, member, snippets)}"
#     try:
#         res = subprocess.run(
#             ["ollama", "run", model],
#             input=prompt.encode("utf-8"),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             timeout=60,
#         )
#         out = res.stdout.decode("utf-8").strip()
#         m = re.search(r"\{.*\}", out, re.S)
#         if m:
#             payload = json.loads(m.group(0))
#             return str(payload.get("answer","")).strip()
#     except Exception as e:
#         print("Ollama error:", e)
#     return "I can’t answer from the available messages."

# app/llm.py
import os
import httpx
import textwrap

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def _build_prompt(question: str, member: str, cands: list[dict], intent: str | None = None) -> str:
    context = "\n".join(
        f"- [{m.get('timestamp','')}] {m.get('user_name','')}: {m.get('message','')}"
        for m in cands
    )
    intent_hint = ""
    if intent == "WHEN":
        intent_hint = "If you answer, return only a time or date phrase."
    elif intent == "WHERE":
        intent_hint = "If you answer, return only a location or place name."
    elif intent == "COUNT":
        intent_hint = "If you answer, return only a number."
    elif intent == "FAVORITES":
        intent_hint = "If you answer, return only the relevant item names."

    return textwrap.dedent(f"""
    You are a precise data extraction assistant.
    Use ONLY the messages below to answer the question.
    If the answer is not clearly stated, reply exactly with: Unknown.

    Member: {member}
    Messages:
    {context}

    Question: {question}
    {intent_hint}

    Answer (short, no extra explanation; reply 'Unknown' if not present):
    """).strip()

def ollama_answer(question: str, member: str, cands: list[dict], model: str | None = None, intent: str | None = None) -> str | None:
    model = model or DEFAULT_MODEL
    prompt = _build_prompt(question, member, cands, intent=intent)

    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            r.raise_for_status()
            out = (r.json().get("response") or "").strip()
    except Exception:
        return None

    if not out:
        return None

    if out.lower().startswith("unknown"):
        return None

    # one short line
    return out.splitlines()[0][:300]
