import os
import json
import fitz
import pandas as pd
import requests
from tqdm import tqdm

INPUT_FILE = "data/04_selected_with_pdfs.xlsx"
OUTPUT_FILE = "data/05_ai_summaries_v2.xlsx"

TEXT_DIR = "texts"
SUMMARY_DIR = "summaries_v2"
JSON_DIR = "json_summaries"

OLLAMA_MODEL = "qwen2.5:7b"

os.makedirs("data", exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)


def ask_ollama(prompt, temperature=0.2, timeout=900):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        },
        timeout=timeout
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()["response"]


def extract_text_from_pdf(pdf_path):
    text = ""

    try:
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            text += f"\n\n--- PAGE {page_num + 1} ---\n"
            text += page_text
        doc.close()
    except Exception as e:
        print(f"PDF extract error: {pdf_path} | {e}")

    return text


def chunk_text(text, max_chars=12000):
    paragraphs = text.split("\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) < max_chars:
            current += para + "\n"
        else:
            chunks.append(current)
            current = para + "\n"

    if current.strip():
        chunks.append(current)

    return chunks


def safe_filename(title):
    title = str(title).lower()
    title = "".join(c if c.isalnum() else "_" for c in title)
    title = "_".join(title.split("_"))
    return title[:80]


def summarize_chunk(title, chunk, chunk_id, total_chunks):
    prompt = f"""
You are an AI research assistant for Fake News Detection literature review.

You are reading ONE CHUNK of a scientific paper.

Paper title:
{title}

Chunk {chunk_id}/{total_chunks}

Task:
Extract only information explicitly stated in this chunk.

Return in Vietnamese.

Use this format:

[CHUNK SUMMARY]

Problem:
- ...

Dataset:
- ...

Method:
- ...

Baseline:
- ...

Metrics:
- ...

Results:
- ...

Limitations:
- ...

Future Work:
- ...

Important Evidence:
- Quote or paraphrase important evidence from this chunk.

If information is missing in this chunk, write "Không thấy trong chunk này".

Chunk text:
{chunk}
"""

    return ask_ollama(prompt)


def final_structured_summary(title, chunk_summaries):
    joined = "\n\n".join(chunk_summaries)

    prompt = f"""
You are a senior NLP researcher.

Based ONLY on the chunk summaries below, create a structured JSON summary for the paper.

Paper title:
{title}

Important rules:
- Return valid JSON only.
- Do not use markdown.
- Do not invent missing information.
- If unknown, use "not_found".
- Use Vietnamese for text values.
- Arrays must be arrays, not strings.

JSON schema:

{{
  "title": "",
  "problem": "",
  "dataset": [],
  "method": "",
  "baseline": [],
  "metrics": [],
  "results": "",
  "limitations": [],
  "future_work": [],
  "research_gap_signals": [],
  "reliability_notes": ""
}}

Chunk summaries:
{joined}
"""

    raw = ask_ollama(prompt)

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        json_text = raw[start:end]
        data = json.loads(json_text)
        return data, raw
    except Exception:
        data = {
            "title": title,
            "problem": "json_parse_failed",
            "dataset": [],
            "method": "json_parse_failed",
            "baseline": [],
            "metrics": [],
            "results": "json_parse_failed",
            "limitations": [],
            "future_work": [],
            "research_gap_signals": [],
            "reliability_notes": raw
        }
        return data, raw


df = pd.read_excel(INPUT_FILE)

records = []

for i, row in tqdm(df.iterrows(), total=len(df)):
    title = row.get("title", f"paper_{i+1}")
    pdf_path = row.get("local_pdf_path", "")

    record = row.to_dict()

    if not isinstance(pdf_path, str) or not os.path.exists(pdf_path):
        record["summary_status"] = "pdf_not_found"
        records.append(record)
        continue

    text = extract_text_from_pdf(pdf_path)

    if len(text.strip()) < 1000:
        record["summary_status"] = "text_too_short"
        records.append(record)
        continue

    filename = safe_filename(title)

    text_path = os.path.join(TEXT_DIR, f"{i+1:02d}_{filename}.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)

    chunks = chunk_text(text, max_chars=12000)

    chunk_summaries = []

    for chunk_id, chunk in enumerate(chunks[:8], start=1):
        try:
            chunk_summary = summarize_chunk(title, chunk, chunk_id, min(len(chunks), 8))
        except Exception as e:
            chunk_summary = f"Chunk summarization failed: {e}"

        chunk_summaries.append(chunk_summary)

    data, raw_final = final_structured_summary(title, chunk_summaries)

    json_path = os.path.join(JSON_DIR, f"{i+1:02d}_{filename}.json")
    md_path = os.path.join(SUMMARY_DIR, f"{i+1:02d}_{filename}.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(raw_final)

    record["summary_status"] = "success"
    record["problem"] = data.get("problem")
    record["dataset"] = json.dumps(data.get("dataset", []), ensure_ascii=False)
    record["method"] = data.get("method")
    record["baseline"] = json.dumps(data.get("baseline", []), ensure_ascii=False)
    record["metrics"] = json.dumps(data.get("metrics", []), ensure_ascii=False)
    record["results"] = data.get("results")
    record["limitations"] = json.dumps(data.get("limitations", []), ensure_ascii=False)
    record["future_work"] = json.dumps(data.get("future_work", []), ensure_ascii=False)
    record["research_gap_signals"] = json.dumps(data.get("research_gap_signals", []), ensure_ascii=False)
    record["reliability_notes"] = data.get("reliability_notes")

    records.append(record)

out_df = pd.DataFrame(records)
out_df.to_excel(OUTPUT_FILE, index=False)

print("Saved:", OUTPUT_FILE)
print("Success:", (out_df["summary_status"] == "success").sum())