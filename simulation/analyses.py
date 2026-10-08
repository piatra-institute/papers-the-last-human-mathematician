"""Corpus analysis for "1976-2036: From the Last Human Computer to the Last Human Mathematician".

Reads only the frozen files in data/ (see fetch_data.py) and measures three things:
  computer       when the unqualified noun "computer" came to denote machines in printed English, by three criteria:
                 the share of uses that the pre-war human sense can account for, the rate at which writers marked the
                 machine sense with a qualifier ("electronic", "digital", "automatic"), and the rate at which they
                 marked the human sense ("human computer"), net of "human-computer interaction/interface"
  typewriter     the same marking pattern for a second noun that once named both a machine and its operator
  mathematician  the corresponding rates for "mathematician" in books to 2022 and in titles and abstracts of scholarly
                 works to October 2026
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

DATA = Path(__file__).parent / "data"


def _load():
    ng = json.loads((DATA / "ngram.json").read_text())
    oc = json.loads((DATA / "openalex_counts.json").read_text())
    oh = json.loads((DATA / "openalex_human_mathematician.json").read_text())
    return ng, oc, oh


def _group(ng, name):
    g = ng["groups"][name]
    y0, y1 = g["years"]
    years = np.arange(y0, y1 + 1)
    s = {k: np.array(v, dtype=float) for k, v in g["series"].items()}
    return years, s


def window_ratio(num, den, half=2):
    """Ratio of centred moving sums (window 2*half+1 years); NaN where the denominator is zero."""
    k = np.ones(2 * half + 1)
    n = np.convolve(num, k, mode="same")
    d = np.convolve(den, k, mode="same")
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.where(d > 0, n / d, np.nan)
    r[:half] = np.nan
    r[-half:] = np.nan
    return r


def smooth(x, half=1):
    k = np.ones(2 * half + 1) / (2 * half + 1)
    y = np.convolve(x, k, mode="same")
    y[:half] = np.nan
    y[-half:] = np.nan
    return y


def first_persistent(years, values, threshold, above=True):
    """First year from which values stay above (or below) threshold in every later year with data (NaN = no data)."""
    v = np.asarray(values, dtype=float)
    ok = np.isnan(v) | ((v >= threshold) if above else (v < threshold))
    hit = ~np.isnan(v) & ((v >= threshold) if above else (v < threshold))
    for i in range(len(years)):
        if hit[i] and ok[i:].all():
            return int(years[i])
    return None


def computer(ng):
    years, s = _group(ng, "computer")
    fc = s["computer"] + s["computers"]
    qm = sum(s[k] for k in ("electronic computer", "electronic computers", "digital computer", "digital computers",
                            "automatic computer", "automatic computers"))
    hci = sum(s[k] for k in ("human computer interaction", "human computer interface", "human computer interfaces",
                             "human computer interactions"))
    qh = np.clip(s["human computer"] + s["human computers"] - hci, 0, None)
    cm = s["computing machine"] + s["computing machines"]
    m = window_ratio(qm, fc)
    h = window_ratio(qh, fc)
    i = lambda y: int(y - years[0])
    # machine share of uses: the human sense cannot exceed its pre-war frequency (low) or its wartime peak (high)
    b_low = float(np.mean(fc[i(1902):i(1932) + 1]))
    fc3 = smooth(fc, 1)
    b_high = float(np.nanmax(fc3[i(1940):i(1946) + 1]))
    share = {}
    for name, b in (("low", b_low), ("high", b_high)):
        share[name] = {"baseline": b,
                       "year_half": first_persistent(years, fc3, 2 * b),
                       "year_ninety": first_persistent(years, fc3, 10 * b)}
    win = (years >= 1940) & (years <= 2000)
    mw = np.where(win, m, np.nan)
    peak_i = int(np.nanargmax(mw))
    peak_y, peak_v = int(years[peak_i]), float(m[peak_i])
    after = years > peak_y
    fall = {}
    for frac in (0.5, 0.25, 0.1):
        fall[str(frac)] = first_persistent(years[after], m[after], frac * peak_v, above=False)
    hw = (years >= 1940) & (years <= 1975)
    hpk = int(np.nanargmax(np.where(hw, h, np.nan)))
    out = {
        "years": years, "fc": fc, "m": m, "h": h,
        "fc_1930s_mean": float(np.mean(fc[i(1930):i(1939) + 1])), "fc_1960": float(fc[i(1960)]),
        "growth_1940_1960": float(fc[i(1960)] / fc[i(1940)]),
        "share": share,
        "m_peak_year": peak_y, "m_peak": peak_v, "m_fall_years": fall,
        "m_1976": float(m[i(1976)]), "m_1976_over_peak": float(m[i(1976)] / peak_v),
        "m_2000": float(m[i(2000)]),
        "h_peak_year_1940_1975": int(years[hpk]), "h_peak_1940_1975": float(h[hpk]),
        "h_1972": float(h[i(1972)]), "h_2018": float(h[i(2018)]),
        "h_2018_over_1972": float(h[i(2018)] / h[i(1972)]),
        "m_1950": float(m[i(1950)]), "h_1950": float(h[i(1950)]), "m_over_h_1950": float(m[i(1950)] / h[i(1950)]),
        "computing_machine_share_1940": float(cm[i(1940)] / (cm[i(1940)] + fc[i(1940)])),
        "computing_machine_share_1960": float(cm[i(1960)] / (cm[i(1960)] + fc[i(1960)])),
    }
    return out


def typewriter(ng):
    years, s = _group(ng, "typewriter")
    ft = s["typewriter"] + s["typewriters"]
    fty = s["typist"] + s["typists"]
    person = s["typewriter girl"] + s["typewriter girls"] + s["lady typewriter"] + s["lady typewriters"]
    p = window_ratio(person, ft)
    r = window_ratio(fty, ft)
    w = (years >= 1880) & (years <= 1940)
    pk = int(np.nanargmax(np.where(w, p, np.nan)))
    i = lambda y: int(y - years[0])
    return {"years": years, "person_rate": p, "typist_ratio": r,
            "person_peak_year": int(years[pk]), "person_peak": float(p[pk]),
            "person_1930": float(p[i(1930)]), "person_1930_over_peak": float(p[i(1930)] / p[pk]),
            "typist_ratio_1890": float(r[i(1890)]), "typist_ratio_1920": float(r[i(1920)]),
            "typist_ratio_1940": float(r[i(1940)])}


def mathematician_books(ng):
    years, s = _group(ng, "mathematician")
    fm = s["mathematician"] + s["mathematicians"]
    hq = s["human mathematician"] + s["human mathematicians"]
    mq = sum(s[k] for k in ("automated mathematician", "artificial mathematician", "machine mathematician",
                            "computer mathematician", "robot mathematician", "mechanical mathematician",
                            "electronic mathematician", "AI mathematician"))
    h = window_ratio(hq, fm)
    mm = window_ratio(mq, fm)
    i = lambda y: int(y - years[0])
    return {"years": years, "h": h, "m": mm,
            "h_1960": float(h[i(1960)]), "h_1990": float(h[i(1990)]), "h_2018": float(h[i(2018)]),
            "m_2018": float(mm[i(2018)]), "m_max": float(np.nanmax(mm)), "m_max_year": int(years[np.nanargmax(mm)]),
            "h_max": float(np.nanmax(h)), "h_over_m_2018": float(h[i(2018)] / mm[i(2018)])}


def mathematician_scholarly(oc, oh):
    q = oc["queries"]
    yrs = list(range(2016, 2027))
    base = {y: q["mathematician"].get(str(y), 0) for y in yrs}
    hum = {y: q["human mathematician"].get(str(y), 0) for y in yrs}
    machine_keys = ("AI mathematician", "automated mathematician", "artificial mathematician", "machine mathematician",
                    "robot mathematician")
    mac = {y: sum(q[k].get(str(y), 0) for k in machine_keys) for y in yrs}
    agent = {y: q["mathematical agent"].get(str(y), 0) for y in yrs}
    pre = [y for y in yrs if y <= 2024]
    pre_mean = float(np.mean([hum[y] for y in pre]))
    pre_rate = float(np.sum([hum[y] for y in pre]) / np.sum([base[y] for y in pre]))
    # record-level cleaning for "human mathematician"
    recs = oh["records"]
    norm = lambda t: re.sub(r"[^a-z0-9]", "", (t or "").lower())
    clean = {}
    for y in yrs:
        R = [r for r in recs if r["year"] == y]
        seen, U = set(), []
        for r in R:
            k = norm(r["title"])
            if k and k in seen:
                continue
            seen.add(k)
            U.append(r)
        Uc = [r for r in U if not r["single_author_cluster"]]
        ph = [r for r in Uc if r["phrase_in_text"]]
        ai = [r for r in ph if r["ai_context"]]
        clean[y] = {"raw": len(R), "unique": len(U), "excluding_cluster": len(Uc), "phrase": len(ph), "ai_context": len(ai),
                    "cluster_raw": sum(r["single_author_cluster"] for r in R),
                    "cluster_unique": sum(r["single_author_cluster"] for r in U)}
    pre_clean = float(np.mean([clean[y]["phrase"] for y in pre]))
    pre_clean_rate = float(np.sum([clean[y]["phrase"] for y in pre]) / np.sum([base[y] for y in pre]))
    recent = [2025, 2026]
    ai_share_recent = (sum(clean[y]["ai_context"] for y in recent) / max(1, sum(clean[y]["phrase"] for y in recent)))
    ai_share_pre = (sum(clean[y]["ai_context"] for y in pre) / max(1, sum(clean[y]["phrase"] for y in pre)))
    return {"years": yrs, "mathematician": base, "human": hum, "machine": mac, "agent": agent,
            "human_rate": {y: hum[y] / base[y] for y in yrs}, "machine_rate": {y: mac[y] / base[y] for y in yrs},
            "pre_mean_count": pre_mean, "pre_rate": pre_rate, "rate_2026": hum[2026] / base[2026],
            "fold_2026_raw": hum[2026] / pre_mean, "clean": clean, "pre_mean_clean": pre_clean,
            "clean_rate_2026": clean[2026]["phrase"] / base[2026], "pre_clean_rate": pre_clean_rate,
            "clean_rate_fold": (clean[2026]["phrase"] / base[2026]) / pre_clean_rate,
            "fold_2026_clean": clean[2026]["phrase"] / pre_clean,
            "ai_share_2025_2026": ai_share_recent, "ai_share_2016_2024": ai_share_pre,
            "machine_total_2016_2026": int(sum(mac.values())), "machine_2026": mac[2026],
            "machine_over_human_2026": mac[2026] / clean[2026]["phrase"], "machine_rate_2026": mac[2026] / base[2026],
            "retrieved": oc["retrieved"]}


def run():
    ng, oc, oh = _load()
    c = computer(ng)
    t = typewriter(ng)
    mb = mathematician_books(ng)
    ms = mathematician_scholarly(oc, oh)
    checks = {
        "computer_frequency_grew_twentyfold_1940_1960": c["growth_1940_1960"] > 20,
        "machine_majority_by_1955_even_with_wartime_baseline": c["share"]["high"]["year_half"] is not None
        and c["share"]["high"]["year_half"] <= 1955,
        "machine_marking_peaked_in_the_1950s": 1950 <= c["m_peak_year"] <= 1960,
        "machine_marking_below_tenth_of_peak_before_1985": c["m_fall_years"]["0.1"] is not None
        and c["m_fall_years"]["0.1"] < 1985,
        "contrastive_human_marking_peaked_before_machine_marking": c["h_peak_year_1940_1975"] < c["m_peak_year"],
        "retrospective_human_marking_rose_after_1972": c["h_2018_over_1972"] > 2,
        "typewriter_person_marking_peaked_1890_1910": 1890 <= t["person_peak_year"] <= 1910,
        "typist_displaced_person_sense": t["typist_ratio_1940"] > 5 * t["typist_ratio_1890"],
        "books_mark_the_human_more_than_the_machine_in_2018": mb["h_over_m_2018"] > 3,
        "human_mathematician_rose_in_scholarly_titles": ms["fold_2026_clean"] > 5,
        "recent_human_marking_is_contrastive": ms["ai_share_2025_2026"] >= 0.85,
        "marking_pattern_inverted_relative_to_1950": c["m_over_h_1950"] > 10 and ms["machine_over_human_2026"] < 1,
    }
    return {"computer": c, "typewriter": t, "mathematician_books": mb, "mathematician_scholarly": ms,
            "data": {"ngram_retrieved": ng["retrieved"], "ngram_corpus": ng["corpus"],
                     "openalex_retrieved": oc["retrieved"]},
            "checks": {k: bool(v) for k, v in checks.items()}}
