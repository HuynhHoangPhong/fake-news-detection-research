import os
import pandas as pd
import requests

INPUT_FILE = "data/05_ai_summaries.xlsx"
OUTPUT_FILE = "data/06_research_gap_and_ideas.md"

OLLAMA_MODEL = "qwen2.5-coder:7b"

os.makedirs("data", exist_ok=True)


def ask_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        },
        timeout=900
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()["response"]


df = pd.read_excel(INPUT_FILE)

content = ""

for idx, row in df.iterrows():
    summary = str(row.get("ai_summary", ""))

    if (
        summary == "PDF not found"
        or "Summarization failed" in summary
        or "Text extraction failed" in summary
        or len(summary.strip()) < 100
    ):
        continue

    content += f"""
=== PAPER {idx + 1} ===
Title: {row.get('title')}
Venue: {row.get('venue')}
Year: {row.get('year')}
Citation: {row.get('citation_count')}
Trust score: {row.get('trust_score')}

Summary:
{summary[:8000]}
"""

prompt = f"""
Bạn là một nhà nghiên cứu NLP cao cấp trong lĩnh vực Fake News Detection trên mạng xã hội.

Dựa trên các paper đã được lọc và tóm tắt bên dưới, hãy phân tích nghiêm túc:

1. Các hướng nghiên cứu chính
2. Dataset thường dùng
3. Model / phương pháp thường dùng
4. Hạn chế lặp lại nhiều nhất giữa các paper
5. Research gap quan trọng nhất
6. 5 ý tưởng cải tiến mới
7. Chọn 1 ý tưởng khả thi nhất cho sinh viên
8. Đề xuất kiến trúc mô hình
9. Đề xuất baseline cần so sánh
10. Đề xuất metrics đánh giá
11. Đề xuất ablation study
12. Đề xuất tên đề tài tiếng Việt và tiếng Anh

Yêu cầu bắt buộc:
- Không bịa paper.
- Không bịa kết quả thực nghiệm.
- Mọi nhận định phải dựa trên summary bên dưới.
- Nếu thiếu dữ liệu thì ghi rõ "Dữ liệu hiện tại chưa đủ".
- Ưu tiên ý tưởng có thể làm được với tài nguyên sinh viên.
- Trình bày bằng tiếng Việt rõ ràng.

PAPERS:
{content}
"""

result = ask_ollama(prompt)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(result)

print(result)
print("Saved:", OUTPUT_FILE)