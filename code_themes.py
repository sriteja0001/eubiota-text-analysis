"""LLM-coded themes for the feedback corpus (auditable artifact).

Each of the 86 UNIQUE feedback strings was read and coded by an LLM (Claude Opus 4.8) into:
  - theme  : one of 10 quality themes (see THEMES)
  - target : 'winner' (the chosen response) or 'loser' (the rejected response)
  - valence: 'pos' (a strength / praise) or 'neg' (a weakness / criticism)

Tag shorthand used below: <theme>:<W|L><+|->
  W+ = winner strength (praise of the chosen answer)   -> the key "genuine positive"
  W- = winner weakness (mild criticism of the chosen answer)
  L- = loser weakness  (criticism of the rejected answer)   -> NOT a positive for the winner
  L+ = loser strength  (acknowledged strength of the rejected answer)

Run:  python code_themes.py   ->  writes data/feedback_theme_codes.csv
Re-coding when the corpus grows: the script asserts the unique-feedback count; if it
changes, re-code (or use the optional Anthropic-API cell documented in the notebook).
"""
import re
from pathlib import Path
import pandas as pd

DATA = Path("data")
CUR = DATA / "ANONYMOUS Human study results_revision - current data.csv"
PREV = DATA / "ANONYMOUS Human study results_revision - Previous data.csv"

THEMES = {  # abbreviation -> full label
    "cit": "citation_evidence", "tra": "transparency_trace", "tho": "detail_thoroughness",
    "spe": "specificity", "con": "conciseness_directness", "cla": "clarity_structure",
    "acc": "accuracy_correctness", "act": "actionability",
    "uns": "fewer_unsupported_claims", "ret": "retrieval_tool_failure",
}

# index (into the deterministic unique-feedback order) -> space-separated tags
CODES = {
    0: "tho:W+ spe:W+ tra:W+", 1: "tho:W+", 2: "tra:W+", 3: "cla:W+", 4: "uns:W+ cit:W+",
    5: "con:W+", 6: "cit:W+", 7: "cit:W+", 8: "tra:W+ cit:W+ act:W+ cit:L-",
    9: "acc:W+ tho:W+ cit:W-", 10: "acc:W+ ret:L- acc:L- cit:L-", 11: "cit:W+ tra:W+ cit:L-",
    12: "tra:W+ cit:W+ cla:W+", 13: "tra:W+ cit:W+ cit:L-", 14: "acc:W+ ret:L- acc:L-",
    15: "acc:W+ spe:W+ acc:L-", 16: "acc:W+ spe:W+", 17: "cit:W+ spe:W+ tra:W+ cit:L-",
    18: "tra:W+ ret:W-", 19: "cla:W+", 20: "tra:W+ ret:W-", 21: "cit:W+ tra:W+ ret:W-",
    22: "cit:W+ cit:L-", 23: "cit:W+ cla:W+", 24: "con:W+ cit:W+", 25: "cit:W+ tra:W+ cit:L-",
    26: "cit:W+ cit:L-", 27: "tra:W+ cit:W+ act:W+", 28: "spe:W+ acc:W+ acc:L-",
    29: "spe:W+ tho:W+ cla:W+", 30: "cla:W+ tho:W+ spe:W+ act:W+ cit:W- tra:W-",
    31: "cit:W+ tra:W+ con:W-", 32: "tra:W+ cit:W+ tho:W+ act:W+", 33: "con:W+ cit:W+ cla:W+ act:W+",
    34: "con:W+ spe:W+ cit:W+ act:W+", 35: "cla:W+ cit:W+ cit:L-", 36: "tho:W+ cit:W+",
    37: "cla:W+ tra:W+ cit:W+ act:W+", 38: "cla:W+ tho:W+", 39: "acc:W+",
    40: "acc:W+ spe:W+ act:W+ tho:L-", 41: "cla:W+ cit:W+ tra:W+",
    42: "cla:W+ tra:W+ cit:W+ con:W+ act:W+", 43: "cit:W+ cla:W+", 44: "act:W+ acc:W+ acc:L-",
    45: "tho:W+ act:W+ ret:L- cit:L- cit:W-", 46: "tho:W+ cit:W+ cla:W+ con:L-", 47: "cla:W+ cit:L-",
    48: "con:W+ cit:W+ tra:W+ act:W+ con:L-", 49: "act:W+ tho:W+ spe:W+", 50: "cla:W+",
    51: "tho:W+", 52: "tho:W+ cit:W+ tra:W+", 53: "con:W+", 54: "cla:W+ cit:W+ cit:W-",
    55: "tra:W+ cit:W+ ret:W-", 56: "cit:W+ tra:W+ tho:W-", 57: "tho:W+ tra:W+ cit:W-",
    58: "acc:W+ tra:W+ cit:W+ act:W+", 59: "acc:W+ tho:W+ ret:L-", 60: "tho:W+ spe:W+ act:W+ cit:L-",
    61: "cla:W+ tho:W+ spe:W+ act:W+ tho:L-", 62: "cit:W+ tra:W+", 63: "acc:L-",
    64: "tra:W+ cit:W+ cla:W+", 65: "tra:W+ cit:W+ act:W+ cit:L-", 66: "tho:W+",
    67: "tho:W+ cit:W+ spe:W+ cla:W+", 68: "cla:W+ tra:W+ act:W-", 69: "cit:W+ tra:W+",
    70: "con:W+ cit:W+ cla:W+ act:W+ con:L-", 71: "tho:W+", 72: "cla:W+ con:W+ con:L- cit:L-",
    73: "cit:W+ tho:W+ spe:W+", 74: "cit:W+ tra:W+", 75: "acc:W+ cit:W+ act:W+ cla:W+",
    76: "spe:W+ cit:W- cit:L-", 77: "tho:W+ cit:W-", 78: "tra:W+ cit:W+ acc:W+ act:W+",
    79: "act:W+ cla:W+", 80: "acc:W+", 81: "acc:W+ spe:W+ cla:W+ tho:L- cit:L- cit:W-",
    82: "tra:W+ cit:W+ spe:W-", 83: "cit:W+ tra:W+ act:W+", 84: "cla:W+", 85: "tra:W+ cit:W-",
}


def extract_cur(t):
    t = str(t)
    m = re.search(r"General Feedback:\s*(.*)", t, re.S | re.I)
    return (m.group(1) if m else t).strip()


def build_corpus():
    cur = pd.read_csv(CUR); prev = pd.read_csv(PREV)
    cur_t = pd.DataFrame({"batch": "current", "query": cur["Query"],
                          "user_selected": cur["User Selected"], "system": cur["Actual Winner"],
                          "feedback": cur["Unnamed: 4"].apply(extract_cur)})
    prev_t = pd.DataFrame({"batch": "previous", "query": prev["Query"],
                           "user_selected": prev["User Selected"], "system": prev["Actual Winner"],
                           "feedback": prev["Comment"].astype(str).str.strip()})
    df = pd.concat([cur_t, prev_t], ignore_index=True)
    df["feedback"] = df["feedback"].fillna("").astype(str)
    df["usable"] = (df["feedback"].str.len() > 3) & (df["feedback"] != "-") & (df["feedback"].str.lower() != "nan")
    return df


def unique_ordered(df):
    u = df[df.usable & df.system.isin(["agent", "llm"])].copy()
    g = (u.groupby("feedback")
           .agg(n=("feedback", "size"), system=("system", lambda s: s.value_counts().index[0]))
           .reset_index()
           .sort_values(["n", "feedback"], ascending=[False, True])
           .reset_index(drop=True))
    return g


def main():
    df = build_corpus()
    g = unique_ordered(df)
    assert len(g) == len(CODES) == 86, (
        f"unique-feedback count changed ({len(g)} vs {len(CODES)}). Re-code themes before running.")
    rows = []
    for i, r in g.iterrows():
        for tag in CODES[i].split():
            abbr, tv = tag.split(":")
            rows.append({
                "feedback_id": i, "feedback": r["feedback"], "system": r["system"],
                "n_uses": int(r["n"]), "theme": THEMES[abbr],
                "target": "winner" if tv[0] == "W" else "loser",
                "valence": "pos" if tv[1] == "+" else "neg",
            })
    out = pd.DataFrame(rows)
    DATA.mkdir(exist_ok=True)
    out.to_csv(DATA / "feedback_theme_codes.csv", index=False)
    print(f"wrote data/feedback_theme_codes.csv: {len(out)} tag-rows across {len(g)} unique feedbacks")
    print("theme totals (winner-positive only):")
    print(out[(out.target == "winner") & (out.valence == "pos")]["theme"].value_counts())


if __name__ == "__main__":
    main()
