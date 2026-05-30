import os
import pandas as pd
import requests

INPUT_FILE = "data/05_ai_summaries_v2.xlsx"
OUTPUT_FILE = "data/06_research_gap_v2.md"

OLLAMA_MODEL = "qwen2.5:7b"

os.makedirs("data", exist_ok=True)


def ask_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.25
            }
        },
        timeout=900
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()["response"]


df = pd.read_excel(INPUT_FILE)

df = df[df["summary_status"] == "success"]

content = ""

for idx, row in df.iterrows():
    content += f"""
=== PAPER {idx + 1} ===
Title: {row.get("title")}
Year: {row.get("year")}
Venue: {row.get("venue")}
Citation: {row.get("citation_count")}
Trust score: {row.get("trust_score")}

Problem:
{row.get("problem")}

Dataset:
{row.get("dataset")}

Method:
{row.get("method")}

Baseline:
{row.get("baseline")}

Metrics:
{row.get("metrics")}

Results:
{row.get("results")}

Limitations:
{row.get("limitations")}

Future Work:
{row.get("future_work")}

Research Gap Signals:
{row.get("research_gap_signals")}
"""

prompt = f"""
Bạn là phản biện khoa học và nhà nghiên cứu NLP trong lĩnh vực Fake News Detection.

Dựa CHỈ trên literature matrix bên dưới, hãy tạo phân tích research gap.

Yêu cầu:
- Không bịa paper.
- Không bịa dataset.
- Không bịa kết quả.
- Nếu dữ liệu thiếu, nói rõ.
- Mỗi gap phải có bằng chứng từ ít nhất 2 paper nếu có thể.
- Ưu tiên gap khả thi cho sinh viên.

Trả lời theo format:

# 1. Tổng quan hướng nghiên cứu

# 2. Các nhóm phương pháp chính
Bảng gồm:
- Nhóm phương pháp
- Paper liên quan
- Ưu điểm
- Hạn chế

# 3. Dataset thường gặp
Bảng gồm:
- Dataset
- Paper sử dụng
- Ghi chú

# 4. Hạn chế lặp lại
Bảng gồm:
- Hạn chế
- Paper có nhắc
- Mức độ lặp lại
- Ý nghĩa nghiên cứu

# 5. Research Gap đáng chú ý
Mỗi gap gồm:
- Gap
- Bằng chứng từ paper
- Vì sao quan trọng
- Mức độ khả thi
- Rủi ro

# 6. 5 ý tưởng cải tiến
Mỗi ý tưởng gồm:
- Tên ý tưởng
- Mô tả
- Dựa trên gap nào
- Input
- Model đề xuất
- Baseline
- Metrics
- Độ khó

# 7. Chọn 1 ý tưởng tốt nhất cho sinh viên
Gồm:
- Lý do chọn
- Kiến trúc đề xuất
- Dataset nên dùng
- Baseline
- Metrics
- Ablation study

# 8. Tên đề tài
- Tiếng Việt
- Tiếng Anh

LITERATURE MATRIX:
{content}
"""

result = ask_ollama(prompt)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(result)

print(result)
print("Saved:", OUTPUT_FILE)