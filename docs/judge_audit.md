# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.8 | ✅ Đạt (0.757 ≥ 0.6; 0.857 ≥ 0.8; 0.8 ≥ 0.7) | **dùng** |
| helpful | 100 | 0.375 | 1.0 | 0.3 | ❌ Trượt (R=0.3 < 0.7, κ=0.375 < 0.6) | **loại** |

Ma trận nhầm lẫn:

- tone_ok: tp=24, fp=4, fn=6, tn=66 → judge bỏ sót 6/30 fail thật (fn), báo nhầm 4/70 pass (fp).
- helpful: tp=9, fp=0, fn=21, tn=70 → judge gần như không bao giờ nói FAIL (chỉ bắt được 3/30 case tệ) dù không bao giờ báo nhầm. P=1.0 là **ảo**: precision cao chỉ vì judge hiếm khi nói FAIL. Rogan-Gladen: tỷ lệ fail quan sát 0.09 → hiệu chỉnh 0.30, tức 2/3 lỗi thật bị judge nuốt.

## ≥5 case audit thủ công

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | H-008 (tone) | PASS | FAIL | **Người** | "hoàn tiền cho anh rồi nha, anh check giúp em" — giọng chủ quan, đẩy trách nhiệm kiểm tra lại cho khách; không được gọi là tone chuẩn. Judge bị chữ "hoàn tiền" tích cực làm mờ giọng thiếu chuyên nghiệp. |
| 2 | H-017 (tone) | PASS | FAIL | **Người** | "LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha" — "nha" là khẩu ngữ, lệch tone CSR. Judge cho pass vì câu có số tiền cụ thể (nội dung đúng ≠ tone đúng). |
| 3 | H-029 (tone) | PASS | FAIL | **Người** | "Hệ thống đang xử lý, không cần nhắn thêm" — rep ngắn, không có gì cụ thể, close off cuộc hội thoại; đây là fail cả tone lẫn helpful. Judge chỉ nhìn câu chữ lịch sự nên miss. |
| 4 | H-042 (tone) | FAIL | PASS | **Người** | "đã hoàn 120.000đ, tiền về trong 3–5 ngày" — lịch sự, cụ thể, đúng tone. Judge báo FAIL không có lý do rõ (false positive). |
| 5 | H-051 (tone) | FAIL | PASS | **Người** | "refund 90.000đ cho đơn O-202" — từ "refund" tiếng Anh pha trong câu tiếng Việt; người đánh giá vẫn coi là PASS vì thông tin đủ và giọng ổn. Judge quá khắt khe với từ ngữ. |
| 6 | HL-015 (helpful) | PASS | FAIL | **Người** | "hoàn 55.000đ cho đơn O-112" — O-112 không có trong dữ liệu thế giới (hallucinated order); judge bị con số cụ thể đánh lừa, không kiểm fact. |
| 7 | HL-016 (helpful) | PASS | FAIL | **Người** | Chỉ xin lỗi dăm ba câu, không nêu bước tiếp theo → không helpful. Judge coi lời xin lỗi dài là "giúp ích". |
| 8 | HL-020 (helpful) | PASS | FAIL | **Người** | "hoàn 90.000đ cho đơn O-303" — sai thực tế (O-303 là damage 150.000đ); thông tin sai số tiền làm reply vô dụng. |
| 9 | HL-028 (helpful) | PASS | FAIL | **Người** | Xin lỗi nhưng không hướng dẫn gì tiếp theo → FAIL; judge PASS vì giọng lễ phép. |
| 10 | HL-035 (helpful) | PASS | FAIL | **Người** | "Một lần nữa LogiX xin lỗi..." — thuần kịch bản xin lỗi, không có nội dung hành động; judge không phân biệt được lịch sự ≠ hữu ích. |

## Kết luận
- **helpful bị loại**: recall 0.3 nghĩa là 21/30 reply tệ được judge cho PASS — dùng nó làm gate là chắc chắn nuốt lỗi. Nguyên nhân thấy rõ trong audit: judge helpful chấm dựa trên *giọng* (xin lỗi, lễ phép) chứ không kiểm *nội dung/hành động*; mọi case H-* fail của nó đều là reply lịch sự nhưng không có thông tin cụ thể.
- **tone_ok được dùng** (κ=0.757): vẫn còn 4 fp + 6 fn trên 100 — chỉ tin khi kết hợp với grader code cho mọi thứ đụng tiền/approval/secret; judge tone chỉ chấm chữ đi chữ tiếng (mọi case đều có câu chữ in trong CSV).
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật.
