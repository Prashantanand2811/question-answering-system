# app/llm.py
import os, httpx, textwrap

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def _build_prompt(question: str, member: str, cands: list[dict]) -> str:
    """
    Ground the model on ONLY the retrieved messages. Ask for a concise answer or 'Unknown'.
    """
    context = "\n".join(
        f"- [{m.get('timestamp','')}] {m.get('user_name','')}: {m.get('message','')}"
        for m in cands
    )
    return textwrap.dedent(f"""
    You are a data extraction assistant. Answer the user’s question strictly using ONLY the messages below.
    If the answer is not stated in the messages, reply exactly with: Unknown.

    Member: {member}
    Messages:
    {context}

    Question: {question}
    Answer (concise, one sentence or short phrase; 'Unknown' if not in messages):
    """).strip()

def ollama_answer(question: str, member: str, cands: list[dict], model: str | None = None, timeout: float = 15.0) -> str | None:
    model = model or DEFAULT_MODEL
    prompt = _build_prompt(question, member, cands)

    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    # Keep it extractive & brief
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 64,
                        "stop": ["\n\n", "Messages:", "Question:"]
                    }
                },
            )
            r.raise_for_status()
            out = r.json().get("response", "").strip()
    except Exception:
        return None

    # Guardrail: if model admits lack of info, return None so main falls back
    if not out or out.lower().startswith(("unknown", "not specified", "not mentioned")):
        return None
    # Keep it short
    return out.splitlines()[0][:300]
