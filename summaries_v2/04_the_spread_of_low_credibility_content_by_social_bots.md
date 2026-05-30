```json
{
  "title": "The spread of low-credibility content by social bots",
  "problem": "Nghiên cứu về sự lan truyền của nội dung sai lệch trên mạng xã hội và vai trò của các bot xã hội trong việc lan truyền nội dung này.",
  "dataset": [
    {
      "description": "14 triệu tin nhắn chia sẻ 400.000 bài viết trên Twitter trong 10 tháng từ năm 2016 đến 2017."
    },
    {
      "description": "Tweets đề cập hoặc trả lời người dùng và bao gồm liên kết đến các bài viết sai lệch có độ tin cậy thấp."
    },
    {
      "description": "389,569 bài viết từ 120 nguồn thông tin thấp về mặt tín nhiệm được thu thập từ giữa tháng 5 năm 2016 đến cuối tháng 3 năm 2017."
    },
    {
      "description": "15.053 câu chuyện từ tổ chức kiểm tra sự thật độc lập như snopes.com, politifact.com và factcheck.org."
    }
  ],
  "method": [
    "Sử dụng nền tảng Hoaxy để theo dõi sự lan truyền của các tuyên bố và thuật toán Botometer để phát hiện bot xã hội.",
    "Phân tích mạng retweet dựa trên dữ liệu từ API Twitter.",
    "Sử dụng phương pháp 'dismantling analysis' để phân tích."
  ],
  "baseline": [
    "not_found"
  ],
  "metrics": [
    {
      "description": "Số lượng tweet liên kết đến nguồn tin thấp về mặt tín nhiệm, số tài khoản chia sẻ bài viết."
    },
    {
      "description": "Bot score distributions for accounts spreading content from different low-credibility sources."
    }
  ],
  "results": "Các bot xã hội đã đóng vai trò không cân xứng trong việc lan truyền nội dung từ các nguồn tin thấp về mặt tín nhiệm. Chúng tăng cường sự lan truyền của nội dung này ở giai đoạn ban đầu trước khi một bài viết trở nên phổ biến. Các bot cũng nhắm mục tiêu vào người dùng có nhiều followers thông qua phản hồi và đề cập.",
  "limitations": [
    "not_found"
  ],
  "future_work": [
    "not_found"
  ],
  "research_gap_signals": [
    {
      "description": "Bots target influential users through mentions and replies to create the appearance that low-credibility content is widely shared."
    },
    {
      "description": "The volume of tweets by likely humans scales super-linearly with the volume by likely bots, suggesting amplified reach among humans."
    }
  ],
  "reliability_notes": [
    "Bot score của Twitter accounts is computed using the Botometer classifier which evaluates the extent to which an account exhibits similarity to the characteristics of social bots26."
  ]
}
```