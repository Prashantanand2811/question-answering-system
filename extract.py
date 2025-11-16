# import re
# from dateutil import parser as dateparser

# DATE_PATTERNS = [
#     r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
#     r"aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:,\s*\d{4})?\b",
#     r"\b\d{4}-\d{2}-\d{2}\b",
#     r"\b(?:this|next)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
#     r"\b(?:the\s+)?first\s+week\s+of\s+[A-Za-z]+\b",
# ]

# def find_date_phrase(text: str) -> str | None:
#     for pat in DATE_PATTERNS:
#         m = re.search(pat, text, flags=re.IGNORECASE)
#         if m:
#             return text[m.start():m.end()]
#     return None

# def normalize_favorites_span(text: str) -> str | None:
#     m = re.search(r"favorite(?:s)?[^:]*?(?:are|:)\s*(.+)$", text, flags=re.IGNORECASE)
#     if not m: return None
#     span = m.group(1).strip()
#     span = re.split(r"[.;]", span)[0]  # cut at sentence end
#     return span.strip()

# def extract_answer(question: str, intent: str, snippets: list[dict]) -> str | None:
#     for m in snippets:
#         msg = m.get("message","")
#         if intent == "WHEN":
#             span = find_date_phrase(msg)
#             if span:
#                 try:
#                     dateparser.parse(span, fuzzy=True)
#                     return span
#                 except Exception:
#                     # accept relative phrases like 'next Tuesday'
#                     if re.search(r"(next|this|week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)", span, re.I):
#                         return span
#         elif intent == "COUNT":
#             if re.search(r"\b(car|cars|vehicle|vehicles)\b", msg, flags=re.IGNORECASE):
#                 mnum = re.search(r"\b\d+\b", msg)
#                 if mnum:
#                     return mnum.group(0)
#         elif intent == "FAVORITES":
#             fav = normalize_favorites_span(msg)
#             if fav:
#                 return fav
#     return None
# app/extract.py
import re

MONTHS_PATTERN = r"(January|February|March|April|May|June|July|August|September|October|November|December)"

def _concat_messages(messages: list[dict]) -> str:
    return " ".join(m.get("message", "") for m in messages)

def _try_when(text: str) -> str | None:
    """
    Try to extract time-related phrases from the combined messages text.
    Handles:
      - Month names ("December", "December 5")
      - "first week of December"
      - "this Friday", "next Friday", "next Monday", etc.
      - "this weekend", "next weekend"
      - "tomorrow", "tomorrow evening", "tomorrow morning", etc.
    """
    # 1) Explicit month or month + day
    m = re.search(rf"\b{MONTHS_PATTERN}\b(?:\s+\d{{1,2}})?", text)
    if m:
        return f"The timing mentioned is {m.group(0)}."

    # 2) first/second/last week of <Month>  (e.g. "first week of December")
    m = re.search(
        r"\b(first|second|third|last)\s+week\s+of\s+" + MONTHS_PATTERN,
        text,
        re.IGNORECASE,
    )
    if m:
        return f"The timing mentioned is {m.group(0)}."

    # 3) this/next/last + weekday  (e.g. "next Friday", "this Monday")
    m = re.search(
        r"\b(this|next|last)\s+"
        r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
        text,
        re.IGNORECASE,
    )
    if m:
        return f"The timing mentioned is {m.group(0)}."

    # 4) this/next/last weekend  (e.g. "next weekend")
    m = re.search(
        r"\b(this|next|last)\s+weekend\b",
        text,
        re.IGNORECASE,
    )
    if m:
        return f"The timing mentioned is {m.group(0)}."

    # 5) tomorrow / today / tonight etc.
    # Covers: "tomorrow", "tomorrow evening", "tomorrow morning", "tomorrow night"
    m = re.search(
        r"\b(tomorrow|today|tonight)\b(?:\s+(morning|afternoon|evening|night))?",
        text,
        re.IGNORECASE,
    )
    if m:
        return f"The timing mentioned is {m.group(0)}."

    # 6) this/next/last week/month/year
    m = re.search(
        r"\b(this|next|last)\s+"
        r"(week|month|year)\b",
        text,
        re.IGNORECASE,
    )
    if m:
        return f"The timing mentioned is {m.group(0)}."

    return None


def _try_where(text: str) -> str | None:
    # in Santorini, to Tokyo, at Le Bernardin, etc.
    m = re.search(r"\b(in|to|at)\s+([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*)", text)
    if m:
        place = m.group(2).strip()
        return f"The location mentioned is {place}."
    return None

def _try_count(text: str) -> str | None:
    m = re.search(r"\b\d+\b", text)
    if m:
        return f"The count mentioned is {m.group(0)}."
    return None

def _try_favorites(text: str) -> str | None:
    # e.g., "at Le Bernardin", "at The French Laundry"
    cands = re.findall(r"\bat\s+([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*)", text)
    if cands:
        # dedupe while preserving order
        uniq = []
        for c in cands:
            if c not in uniq:
                uniq.append(c)
        return "Some favorites mentioned are: " + ", ".join(uniq)
    return None

def extract_answer(question: str, intent: str, messages: list[dict]) -> str | None:
    if not messages:
        return None

    text = _concat_messages(messages)

    if intent == "WHEN":
        ans = _try_when(text)
        if ans:
            return ans

    elif intent == "WHERE":
        ans = _try_where(text)
        if ans:
            return ans

    elif intent == "COUNT":
        ans = _try_count(text)
        if ans:
            return ans

    elif intent == "FAVORITES":
        ans = _try_favorites(text)
        if ans:
            return ans

    # WHAT / OTHER or failed extraction: just give the best message
    best_msg = messages[0].get("message", "").strip()
    if best_msg:
        return best_msg

    return None
