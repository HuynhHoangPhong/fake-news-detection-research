import os
import re
import requests
import pandas as pd
from tqdm import tqdm

INPUT_FILE = "data/03_selected_20_papers.xlsx"
OUTPUT_FILE = "data/04_selected_with_pdfs.xlsx"
PDF_DIR = "papers"

os.makedirs(PDF_DIR, exist_ok=True)

def safe_filename(title):
    title = str(title).lower()
    title = re.sub(r"[^a-z0-9]+", "_", title)
    title = title.strip("_")
    return title[:80]

def download_pdf(url, save_path):
    if not isinstance(url, str) or not url.startswith("http"):
        return False

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            return False

        content_type = response.headers.get("Content-Type", "").lower()

        if "pdf" not in content_type and not response.content.startswith(b"%PDF"):
            return False

        with open(save_path, "wb") as f:
            f.write(response.content)

        return True

    except Exception as e:
        print("Download error:", e)
        return False

df = pd.read_excel(INPUT_FILE)

local_paths = []
download_status = []

for i, row in tqdm(df.iterrows(), total=len(df)):
    title = row.get("title", f"paper_{i+1}")
    pdf_url = row.get("pdf_url")

    filename = f"{i+1:02d}_{safe_filename(title)}.pdf"
    save_path = os.path.join(PDF_DIR, filename)

    if os.path.exists(save_path):
        local_paths.append(save_path)
        download_status.append("already_exists")
        continue

    success = download_pdf(pdf_url, save_path)

    if success:
        local_paths.append(save_path)
        download_status.append("downloaded")
    else:
        local_paths.append("")
        download_status.append("failed")

df["local_pdf_path"] = local_paths
df["pdf_download_status"] = download_status

df.to_excel(OUTPUT_FILE, index=False)

print("Saved:", OUTPUT_FILE)
print(df["pdf_download_status"].value_counts())