# TinySteps — Data Pipeline Project Spec

## Dự án là gì

TinySteps là app học tiếng Anh dành cho giáo viên Việt Nam — những người đang được yêu cầu sử dụng tiếng Anh như ngôn ngữ thứ 2 trong trường học. App theo triết lý "tưởng dễ nên học được": bắt đầu từ bước nhỏ nhất, lặp lại trong bối cảnh thực tế, leo dốc nhẹ đến mức người học không nhận ra mình đang khó lên.

## Mục tiêu của bộ tài liệu này

Tạo toàn bộ **content data** cho app dưới dạng JSON — từ vocabulary, topics, grammar đến lessons hoàn chỉnh. Sau đó export ra dạng text/HTML để giáo viên có thể đọc và review.

## Đối tượng người dùng

- Giáo viên Việt Nam, 25-50 tuổi
- Đã học tiếng Anh ở trường sư phạm nhưng không dùng, quên gần hết
- Cần giao tiếp tiếng Anh trong môi trường trường học
- Tâm lý: sợ sai, ngại nói, không biết bắt đầu từ đâu

## Lộ trình CEFR

App theo framework Cambridge, chia 5 giai đoạn:

| Giai đoạn | Level | Mô tả | Vocab ước tính |
|-----------|-------|-------|----------------|
| Starters | Pre-A1 | Từ vựng cơ bản nhất, câu cực ngắn | ~300 từ |
| Movers | A1 | Câu dài hơn, quá khứ đơn giản | ~400 từ |
| Flyers | A2 | Giao tiếp cơ bản, email đơn giản | ~500 từ |
| KET | A2+ | Tự tin trong công việc hàng ngày | ~400 từ |
| PET | B1 | Trình bày ý kiến, viết báo cáo ngắn | ~500 từ |

Tổng: 2100 từ, 175 lessons (số liệu chốt theo dữ liệu thực tế trong `tinysteps-data/`, verify 2026-07-13).

## 12 Modules (chủ đề)

### Nhóm trường học (50%)
1. **Before class** — Chuẩn bị trước giờ dạy
2. **In class** — Giao tiếp trong lớp học
3. **Giving instructions** — Hướng dẫn học sinh làm bài
4. **Checking understanding** — Kiểm tra học sinh hiểu chưa
5. **Praise & correction** — Khen ngợi và sửa lỗi
6. **School communication** — Họp phụ huynh, email, trao đổi đồng nghiệp

### Nhóm sinh hoạt (50%)
7. **At the market** — Đi chợ, mua sắm
8. **At a restaurant** — Gọi món, thanh toán
9. **Travel & directions** — Du lịch, hỏi đường
10. **Phone calls** — Gọi điện thoại
11. **Health & doctor** — Sức khỏe, khám bệnh
12. **Social conversations** — Giao tiếp xã hội, chào hỏi

## 4 Nguyên tắc thiết kế nội dung

1. **Bắt đầu dễ đến mức không thể từ chối.** Bài đầu tiên hoàn thành trong 2 phút.
2. **Không dạy grammar trực tiếp.** Grammar được nhúng vào bối cảnh, hấp thụ qua lặp lại.
3. **Spiral progression.** Cùng topic quay lại nhiều lần, phức tạp dần. Ví dụ: "Food" ở Starters là "I like rice", ở Flyers là "I'd prefer the grilled chicken, please".
4. **Mỗi bài có bối cảnh thực.** Không drill từ lẻ. Luôn có tình huống cụ thể.

## Nguồn data

1. **CEFR-SP** (github.com/yukiar/CEFR-SP) — 17.000 câu tiếng Anh đã gán nhãn CEFR bởi chuyên gia giáo dục. Lọc câu A1/A2/B1 để dùng làm nguyên liệu.
2. **Cambridge Wordlists** — Official vocabulary lists cho Starters/Movers/Flyers/KET/PET. Convert từ PDF sang JSON.
3. **AI Generate** — Dùng AI tạo dialogues, exercises, reading passages dựa trên vocabulary và grammar constraints.

## Tech stack

- Data format: JSON
- Export format: HTML (đọc trên phone)
- App: Next.js + TypeScript + Tailwind + Supabase
- AI: Gemini API
- SRS: ts-fsrs
- Deploy: Docker + Cloudflare Tunnel

## Cấu trúc thư mục output

```
tinysteps-data/
├── vocabulary/
│   ├── starters.json
│   ├── movers.json
│   ├── flyers.json
│   ├── ket.json
│   └── pet.json
├── topics/
│   └── topics.json
├── grammar/
│   ├── starters.json
│   ├── movers.json
│   ├── flyers.json
│   ├── ket.json
│   └── pet.json
├── lessons/
│   ├── starters/
│   │   ├── lesson-001.json
│   │   ├── lesson-002.json
│   │   └── ...
│   ├── movers/
│   ├── flyers/
│   ├── ket/
│   └── pet/
└── exports/
    ├── vocabulary-overview.html
    ├── lessons-starters.html
    ├── lessons-movers.html
    ├── lessons-flyers.html
    ├── lessons-ket.html
    └── lessons-pet.html
```

## Pipeline thực thi

```
Agent 1 (Vocabulary) → Agent 2 (Topics) → Agent 3 (Grammar) → Agent 4 (Lessons) → Agent 5 (Export)
```

Output của agent trước là input của agent sau. Chạy tuần tự, không song song.
