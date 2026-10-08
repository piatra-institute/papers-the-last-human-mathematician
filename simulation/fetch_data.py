"""Retrieve the corpus data used by analyses.py and freeze it in data/.

Run once (the frozen files are committed); analyses.py reads only data/.

    cd simulation && uv run fetch_data.py

Sources: the Google Books Ngram Viewer JSON endpoint (English corpus, case-insensitive, unsmoothed relative
frequencies) and the OpenAlex works API (title-and-abstract search, grouped by publication year; and the works
matching "human mathematician" in 2016-2026 with flags computed from their titles and abstracts).
"""
from __future__ import annotations

import datetime
import json
import re
import subprocess
import time
import urllib.parse
from pathlib import Path

DATA = Path(__file__).parent / "data"

NGRAM_GROUPS = {
    "computer": (1900, 2022, ["computer", "computers", "electronic computer", "electronic computers", "digital computer",
                              "digital computers", "automatic computer", "automatic computers", "human computer",
                              "human computers", "human computer interaction", "human computer interface",
                              "human computer interfaces", "human computer interactions", "computing machine",
                              "computing machines"]),
    "typewriter": (1860, 1960, ["typewriter", "typewriters", "typist", "typists", "typewriter girl", "typewriter girls",
                                "lady typewriter", "lady typewriters"]),
    "mathematician": (1900, 2022, ["mathematician", "mathematicians", "human mathematician", "human mathematicians",
                                   "automated mathematician", "artificial mathematician", "machine mathematician",
                                   "computer mathematician", "robot mathematician", "mechanical mathematician",
                                   "electronic mathematician", "AI mathematician"]),
}

OPENALEX_QUERIES = {
    "mathematician": "mathematician",
    "human mathematician": '"human mathematician"',
    "AI mathematician": '"AI mathematician"',
    "automated mathematician": '"automated mathematician"',
    "artificial mathematician": '"artificial mathematician"',
    "machine mathematician": '"machine mathematician"',
    "robot mathematician": '"robot mathematician"',
    "mathematical agent": '"mathematical agent"',
}

AI_TERMS = (r"\b(AI|A\.I\.|artificial intelligence|LLMs?|large language models?|language models?|machine learning|neural|"
            r"GPT|transformer|deep learning|automated|automatic|machines?|computers?|algorithms?|agents?|Lean|"
            r"formal(ly)? verif|proof assistant|autoformali|chatbot|ChatGPT|Gemini|Claude|reasoning models?)\b")
PHRASE = r"human[- ]mathematicians?"


def _get(url: str) -> str:
    for _ in range(4):
        out = subprocess.run(["curl", "-s", "-m", "60", "-A", "Mozilla/5.0", url], capture_output=True, text=True).stdout
        if out.strip():
            return out
        time.sleep(3)
    raise RuntimeError(url)


def ngram(phrases, y0, y1):
    q = ",".join(phrases)
    url = ("https://books.google.com/ngrams/json?content=" + urllib.parse.quote(q, safe=",") +
           f"&year_start={y0}&year_end={y1}&corpus=en&smoothing=0&case_insensitive=true")
    rows = json.loads(_get(url))
    # a case-insensitive request returns an "(All)" aggregate for phrases with several case variants, followed by the
    # variants; a phrase with a single variant returns only that row. Prefer the aggregate.
    agg = {r["ngram"][:-len(" (All)")].lower(): r["timeseries"] for r in rows if r["ngram"].endswith(" (All)")}
    single = {}
    for r in rows:
        if not r["ngram"].endswith(" (All)"):
            single.setdefault(r["ngram"].lower(), r["timeseries"])
    return url, {**single, **agg}


def main() -> None:
    DATA.mkdir(exist_ok=True)
    stamp = datetime.date.today().isoformat()
    out = {"retrieved": stamp, "corpus": "Google Books Ngram Viewer, English, case-insensitive, smoothing 0", "groups": {}}
    for name, (y0, y1, phrases) in NGRAM_GROUPS.items():
        series = {}
        for i in range(0, len(phrases), 6):
            url, s = ngram(phrases[i:i + 6], y0, y1)
            # a case-insensitive request returns an "(All)" aggregate for phrases with case variants and the plain
            # series for phrases with a single variant; keep one series per requested phrase
            for p in phrases[i:i + 6]:
                series[p] = s.get(p.lower(), [0.0] * (y1 - y0 + 1))
            time.sleep(2)
        out["groups"][name] = {"years": [y0, y1], "series": series}
    (DATA / "ngram.json").write_text(json.dumps(out))
    counts = {"retrieved": stamp, "source": "OpenAlex works API, title_and_abstract.search grouped by publication_year",
              "queries": {}}
    for k, q in OPENALEX_QUERIES.items():
        url = ("https://api.openalex.org/works?filter=title_and_abstract.search:" + urllib.parse.quote(q) +
               "&group_by=publication_year&per_page=200")
        r = json.loads(_get(url))
        counts["queries"][k] = {g["key"]: g["count"] for g in r["group_by"] if g["key"].isdigit()}
        time.sleep(1)
    (DATA / "openalex_counts.json").write_text(json.dumps(counts))
    # works matching "human mathematician", 2016-2026: identifiers, titles and flags computed from title + abstract
    ai, ph = re.compile(AI_TERMS, re.I), re.compile(PHRASE, re.I)
    cluster = re.compile(r"FBGT|Zhang Xun|张巡", re.I)
    recs = []
    for yr in range(2016, 2027):
        cursor = "*"
        while cursor:
            url = ("https://api.openalex.org/works?filter=publication_year:%d,title_and_abstract.search:%s&per_page=100"
                   "&cursor=%s&select=id,title,publication_year,type,abstract_inverted_index"
                   % (yr, urllib.parse.quote('"human mathematician"'), cursor))
            r = json.loads(_get(url))
            for w in r["results"]:
                ii = w.get("abstract_inverted_index") or {}
                abstract = " ".join(t for p, t in sorted((p, t) for t, ps in ii.items() for p in ps))
                text = (w.get("title") or "") + " " + abstract
                recs.append({"id": w["id"], "year": w["publication_year"], "type": w.get("type"),
                             "title": w.get("title") or "", "phrase_in_text": bool(ph.search(text)),
                             "ai_context": bool(ai.search(text)), "single_author_cluster": bool(cluster.search(text))})
            cursor = r["meta"].get("next_cursor")
            if not r["results"]:
                break
            time.sleep(1)
    (DATA / "openalex_human_mathematician.json").write_text(json.dumps(
        {"retrieved": stamp, "ai_terms": AI_TERMS, "phrase": PHRASE,
         "cluster_rule": "texts containing FBGT or the name of its single author", "records": recs}, ensure_ascii=False))
    print("ngram groups", list(out["groups"]), "openalex records", len(recs))


if __name__ == "__main__":
    main()
