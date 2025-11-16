# app/retrieve.py
import unicodedata
from .nlu import tokenize

def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

def score_overlap(query: str, text: str) -> int:
    q_toks = tokenize(query)
    s = (text or "").lower()
    return sum(t in s for t in q_toks)

def topk_member_messages(
    question: str,
    all_msgs: list[dict],
    member: str,
    k: int = 8
):
    # accent- and case-insensitive equality on user_name
    member_norm = _strip_accents(member.lower())
    cand = []
    for m in all_msgs or []:
        uname = _strip_accents((m.get("user_name") or "").lower())
        if uname == member_norm:
            cand.append(m)

    # sort by (overlap desc, timestamp desc) for stable, useful ranking
    def _key(m):
        overlap = score_overlap(question, m.get("message", ""))
        ts = m.get("timestamp") or ""  # already ISO-ish, string compare is ok for desc if same format
        return (overlap, ts)

    cand.sort(key=_key, reverse=True)
    return cand[:k]
