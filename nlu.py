# app/nlu.py
import re
import unicodedata

STOP = set("the a an to for on at in is are was were of and my your our their his her".split())

def _strip_accents(s: str) -> str:
    # normalize to ascii for easier matching if user omits accents
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

def tokenize(s: str):
    return [t for t in re.findall(r"[a-z0-9']+", s.lower()) if t not in STOP]

def extract_member_name(question: str, names: list[str]) -> str | None:
    """
    Prefer exact full-name match with word boundaries (case-insensitive),
    falling back to unique first-name match. Also try accent-insensitive match.
    """
    q_raw = question
    q = q_raw.lower()
    q_noacc = _strip_accents(q)

    # 1) Full-name match (word boundaries), longest name first
    for n in sorted(names, key=len, reverse=True):
        pat = r"\b" + re.escape(n.lower()) + r"\b"
        if re.search(pat, q):
            return n
        # accent-insensitive fallback
        n_noacc = _strip_accents(n.lower())
        if n_noacc != n.lower():
            pat2 = r"\b" + re.escape(n_noacc) + r"\b"
            if re.search(pat2, q_noacc):
                return n

    # 2) Unique first-name fallback (accent-insensitive)
    first_candidates = []
    for n in names:
        fn = n.split()[0].lower()
        if re.search(r"\b" + re.escape(fn) + r"\b", q):
            first_candidates.append(n)
        else:
            fn_noacc = _strip_accents(fn)
            if fn_noacc != fn and re.search(r"\b" + re.escape(fn_noacc) + r"\b", q_noacc):
                first_candidates.append(n)

    uniq_firsts = {c.split()[0].lower() for c in first_candidates}
    if len(uniq_firsts) == 1 and first_candidates:
        # If only one first name appears and maps to a single full name, return it
        cands = [n for n in names if n.lower().startswith(next(iter(uniq_firsts)))]
        if len(cands) == 1:
            return cands[0]

    return None

def detect_intent(q: str) -> str:
    ql = q.lower()

    if any(phrase in ql for phrase in ["how many", "number of", "count"]):
        return "COUNT"

    if any(word in ql for word in ["favorite", "favourite", "favorites", "favourites"]):
        return "FAVORITES"

    if any(word in ql for word in ["when", "what date", "what day", "which day", "time"]):
        return "WHEN"

    if any(word in ql for word in ["where", "which city", "which country", "which restaurant", "which hotel"]):
        return "WHERE"

    if ql.startswith("what ") or ql.startswith("which "):
        return "WHAT"

    return "OTHER"

