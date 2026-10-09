#!/usr/bin/env python3
"""Parse the narration markdown into voiced segments and synthesise via Fish Audio.

Key comes from FISH_API_KEY only. Chunks are cached by content hash.
"""
import hashlib, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
import requests

SRC = "/root/.claude/uploads/9b852bdd-f834-5d1d-9b84-7e0d081ac7f0/c7a8866b-Returned_Twelve_Dialectics_for_the_Soldier_Who_Came_Home_1.md"
WORK = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(WORK, "cache")
os.makedirs(CACHE, exist_ok=True)

# Voice styles: speed is Fish prosody.speed; temperature lower = steadier
STYLES = {
    "body":      dict(speed=0.92, temperature=0.55, top_p=0.7),
    "heading":   dict(speed=0.88, temperature=0.5,  top_p=0.7),
    "close":     dict(speed=0.84, temperature=0.5,  top_p=0.7),   # italic, second person
    "interlude": dict(speed=0.97, temperature=0.4,  top_p=0.6),   # cooler, steadier briefing
}

# Respellings so the engine reads foreign names cleanly (from the pronunciation guide)
RESPELL = [
    ("whakanoa", "fah-kah-noh-ah"), ("karakia", "kah-rah-kee-ah"), ("kainga", "kah-ee-ngah"),
    ("te ao Maori", "teh ah-oh mah-oh-ree"), ("Maori", "mah-oh-ree"), ("tapu", "tah-poo"), ("noa", "noh-ah"),
    ("Luttwak", "Lut-wak"), ("Hiroo Onoda", "hee-roh-oh oh-noh-dah"), ("Onoda", "oh-noh-dah"),
    ("Lubang", "Loo-bahng"), ("Taleb", "Tah-leb"), ("Heuer", "Hoy-er"), ("Clausewitz", "Klow-zuh-vits"),
    ("Junger", "Jung-er"), ("Sun Tzu", "Soon Dzoo"), ("Stoics", "Stoh-iks"), ("Odysseus", "Oh-diss-ee-us"),
    ("Demodocus", "Deh-mod-uh-kus"), ("Boethius", "Boh-ee-thee-us"), ("Leibniz", "Libe-nits"),
    ("Huayan", "Hwah-yen"), ("Indra", "In-druh"), ("Nyssa", "Niss-uh"),
    ("spiritus contra spiritum", "spee-ri-toos kon-trah spee-ri-toom"), ("Galula", "Gah-loo-lah"),
    ("ananda", "ah-nun-duh"), ("Abhinavagupta", "uh-bhi-nuh-vuh-goop-tuh"), ("Tetlock", "Tet-lock"),
    ("Penelope", "Peh-nel-uh-pee"), ("Jervis", "Jer-vis"), ("Bhagavad Gita", "Bhug-uh-vud Gee-tah"),
    ("Arjuna", "Ar-joo-nuh"), ("Krishna", "Krish-nuh"), ("Karamazov", "Kah-rah-mah-zof"),
    ("Dostoevsky", "Doss-toy-eff-skee"), ("Hegel", "Hay-gul"), ("fana", "fah-nah"), ("baqa", "bah-kah"),
    ("al-Hallaj", "al-hal-lahj"), ("Ramakrishna", "Rah-muh-krish-nuh"), ("Eckhart", "Eck-hart"),
    ("Mao Zedong", "Mow Dzuh-dong"), ("Kuoan", "Kwoh-ahn"), ("Wylie", "Wy-lee"),
    ("Reveille", "ruh-val-ee"), ("Dine", "Dih-neh"),
]


def respell(t):
    for a, b in RESPELL:
        t = re.sub(r"\b" + re.escape(a) + r"\b", b, t)
    return t


def clean(t):
    t = t.replace("\\_", "_").replace("\\[", "[").replace("\\]", "]")
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"\*(.+?)\*", r"\1", t)
    t = re.sub(r"^[#>\s]+", "", t).strip()
    return t


def parse():
    """Return list of segments: dict(kind, style, text, pause_before)."""
    lines = open(SRC, encoding="utf-8").read().split("\n")
    segs = []
    started = False
    quote_buf = []

    def flush_quote():
        nonlocal quote_buf
        if quote_buf:
            txt = " ".join(quote_buf).strip()
            if txt:
                segs.append(dict(kind="para", style="interlude", text=txt, pause=0.9))
            quote_buf = []

    for ln in lines:
        s = ln.rstrip()
        # the spoken piece starts at the italic content note, after the production notes
        if not started:
            if s.startswith("*A note before we begin"):
                started = True
            else:
                continue
        if s.startswith("## Sources for the interludes"):
            flush_quote()
            break
        if not s.strip():
            flush_quote()
            continue
        if s.startswith(">"):
            body = s.lstrip(">").strip()
            if not body:
                flush_quote()
                continue
            if body.startswith("*From "):
                flush_quote()
                continue
            quote_buf.append(clean(body))
            continue
        flush_quote()
        m = re.match(r"^(#+)\s+(.*)$", s)
        if m:
            level, title = len(m.group(1)), clean(m.group(2))
            segs.append(dict(kind="heading", level=level, style="heading", text=title,
                             pause=6.0 if False else 3.5))
            continue
        if s.startswith("*") and s.endswith("*") and not s.startswith("**"):
            segs.append(dict(kind="para", style="close", text=clean(s), pause=0.9))
            continue
        segs.append(dict(kind="para", style="body", text=clean(s), pause=0.9))
    return segs


def mark(segs):
    """Annotate pauses, part names, bed on/off."""
    part = None
    for sg in segs:
        sg["part"] = part
        if sg["kind"] == "heading":
            t = sg["text"]
            if sg["level"] == 3:
                part = t
                sg["part"] = t
            elif sg["level"] == 4 and t.startswith("Interlude"):
                sg["pause"] = 2.8
            if t.startswith("Twelve"):
                sg["pause"] = 9.0   # the longest silence
    # short in-paragraph pause for verse lines in the coda
    return segs


def split_sentences(text, limit=480):
    sents = re.split(r"(?<=[.!?:;])\s+(?=[A-Z\"'(*])", text)
    out, cur = [], ""
    for s in sents:
        if cur and len(cur) + 1 + len(s) > limit:
            out.append(cur)
            cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        out.append(cur)
    return out


def tts(text, style, ref, model="s1", fmt="wav"):
    st = STYLES[style]
    payload = {
        "text": respell(text), "reference_id": ref, "format": fmt, "normalize": True,
        "latency": "normal", "temperature": st["temperature"], "top_p": st["top_p"],
        "prosody": {"speed": st["speed"], "volume": 0}, "chunk_length": 300,
    }
    key = hashlib.sha256(json.dumps([payload, model], sort_keys=True).encode()).hexdigest()[:24]
    path = os.path.join(CACHE, key + "." + fmt)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path
    headers = {"Authorization": "Bearer " + os.environ["FISH_API_KEY"], "Content-Type": "application/json", "model": model}
    for attempt in range(6):
        try:
            r = requests.post("https://api.fish.audio/v1/tts", headers=headers, json=payload, timeout=180)
            if r.status_code == 200 and len(r.content) > 1000:
                open(path, "wb").write(r.content)
                return path
            msg = r.text[:200]
            if r.status_code in (401, 402, 403, 422):
                raise SystemExit(f"Fish API error {r.status_code}: {msg}")
        except requests.RequestException as e:
            msg = str(e)
        time.sleep(2 * (attempt + 1))
    raise SystemExit("Fish API failed repeatedly: " + msg)


if __name__ == "__main__":
    segs = mark(parse())
    print(len(segs), "segments;", sum(len(s["text"]) for s in segs), "chars")
