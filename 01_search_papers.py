import os
import time
import requests
import pandas as pd

os.makedirs("data", exist_ok=True)

QUERIES = [
    "fake news detection graph neural network",
    "fake news detection transformer",
    "fake news detection BERT",
    "fake news detection large language model",
    "fake news detection multimodal",
    "explainable fake news detection",
    "rumor detection graph neural network",
    "misinformation detection social media deep learning",
    "fake news detection propagation network",
    "fake news detection user behavior",
    "fake news detection knowledge graph",
    "fake news detection contrastive learning",
    "fake news detection domain adaptation",
    "fake news detection cross domain",
]

PER_QUERY = 50

url = "https://api.openalex.org/works"

headers = {
    "User-Agent": "fake-news-ai-research/1.0 (mailto:your_email@example.com)"
}

all_rows = []

def reconstruct_abstract(abstract_index):
    if not abstract_index:
        return ""

    words = []
    for word, positions in abstract_index.items():
        for pos in positions:
            words.append((pos, word))

    words = sorted(words)
    return " ".join([word for pos, word in words])


for query in QUERIES:
    print("Searching:", query)

    params = {
        "search": query,
        "per-page": PER_QUERY,
        "filter": "from_publication_date:2016-01-01",
        "sort": "cited_by_count:desc"
    }

    try:
        res = requests.get(url, params=params, headers=headers, timeout=30)
        res.raise_for_status()
        works = res.json().get("results", [])
    except Exception as e:
        print("Search failed:", query, e)
        continue

    for w in works:
        authors = []
        for a in w.get("authorships", [])[:5]:
            author = a.get("author", {})
            if author.get("display_name"):
                authors.append(author["display_name"])

        primary_location = w.get("primary_location") or {}
        source = primary_location.get("source") or {}
        open_access = w.get("open_access") or {}

        all_rows.append({
            "search_query": query,
            "title": w.get("title"),
            "year": w.get("publication_year"),
            "authors": ", ".join(authors),
            "abstract": reconstruct_abstract(w.get("abstract_inverted_index")),
            "citation_count": w.get("cited_by_count", 0),
            "venue": source.get("display_name"),
            "url": w.get("id"),
            "doi": w.get("doi"),
            "is_open_access": open_access.get("is_oa", False),
            "pdf_url": open_access.get("oa_url")
        })

    time.sleep(1)

df = pd.DataFrame(all_rows)

df["dedup_key"] = (
    df["doi"].fillna("").astype(str).str.lower()
    + "___"
    + df["title"].fillna("").astype(str).str.lower()
)

df = df.drop_duplicates(subset=["dedup_key"])
df = df.drop(columns=["dedup_key"])

df.to_excel("data/01_raw_papers.xlsx", index=False)

print("Saved:", len(df), "papers")
print("Output: data/01_raw_papers.xlsx")