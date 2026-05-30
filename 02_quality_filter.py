import os
import pandas as pd

os.makedirs("data", exist_ok=True)

INPUT_FILE = "data/01_raw_papers.xlsx"
SCORED_FILE = "data/02_scored_papers.xlsx"
SELECTED_FILE = "data/03_selected_20_papers.xlsx"

df = pd.read_excel(INPUT_FILE)

TOP_VENUES = [
    "ACL", "EMNLP", "NAACL", "COLING",
    "AAAI", "IJCAI", "NeurIPS", "ICLR", "ICML",
    "KDD", "WWW", "WSDM", "SIGIR", "CIKM",
    "ACM Multimedia", "ACM MM",
    "IEEE", "ACM", "Springer", "Elsevier",
    "Nature", "Scientific Reports"
]

KEYWORDS = [
    "fake news",
    "misinformation",
    "disinformation",
    "rumor detection",
    "social media",
    "graph neural network",
    "gnn",
    "large language model",
    "llm",
    "explainability"
]


def contains_any(text, keywords):
    text = str(text).lower()
    return any(k.lower() in text for k in keywords)


def score_paper(row):
    score = 0
    reasons = []

    venue = str(row.get("venue", "")).lower()
    title = str(row.get("title", "")).lower()
    abstract = str(row.get("abstract", "")).lower()
    url = str(row.get("url", "")).lower()
    doi = str(row.get("doi", "")).lower()

    citations = int(row.get("citation_count", 0) or 0)
    year = int(row.get("year", 0) or 0)

    for v in TOP_VENUES:
        if v.lower() in venue:
            score += 5
            reasons.append(f"trusted venue/source: {v}")
            break

    if contains_any(title + " " + abstract, KEYWORDS):
        score += 3
        reasons.append("topic relevant")

    if citations >= 100:
        score += 3
        reasons.append("citation >= 100")
    elif citations >= 50:
        score += 2
        reasons.append("citation >= 50")
    elif citations >= 10:
        score += 1
        reasons.append("citation >= 10")

    if year >= 2021:
        score += 1
        reasons.append("recent paper")

    if row.get("pdf_url"):
        score += 1
        reasons.append("open access PDF available")

    if "arxiv" in url or "arxiv" in doi:
        score -= 2
        reasons.append("arXiv/preprint caution")

    return score, "; ".join(reasons)


df[["trust_score", "trust_reason"]] = df.apply(
    lambda row: pd.Series(score_paper(row)),
    axis=1
)

df = df.sort_values(
    by=["trust_score", "citation_count", "year"],
    ascending=False
)

df.to_excel(SCORED_FILE, index=False)

selected = df[df["trust_score"] >= 5].head(20)

if len(selected) < 5:
    print("Warning: fewer than 5 papers passed threshold. Lowering threshold to 3.")
    selected = df[df["trust_score"] >= 3].head(20)

selected.to_excel(SELECTED_FILE, index=False)

print("Scored:", len(df), "papers")
print("Selected:", len(selected), "papers")
print("Output:", SCORED_FILE)
print("Output:", SELECTED_FILE)