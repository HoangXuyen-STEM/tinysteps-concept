# Workflow 01 — Vocabulary Agent

## Vai trò
Tạo toàn bộ vocabulary data cho 5 levels (Starters → PET), output JSON theo schema.

## Trigger
Human nói: "Tạo vocabulary data" hoặc "Run Agent 1"

## Skills cần dùng
- @web-scraping hoặc @file-processing (đọc Cambridge wordlists PDF)
- @json-processing (output structured data)
- @english-linguistics (IPA, part of speech)

## Input
- Cambridge official wordlists (PDF hoặc text)
- CEFR-SP dataset từ github.com/yukiar/CEFR-SP (câu đã gán nhãn CEFR)
- Schema: `schemas/vocabulary.schema.json`
- Rules: `RULES.md`

## Output
- `tinysteps-data/vocabulary/starters.json`
- `tinysteps-data/vocabulary/movers.json`
- `tinysteps-data/vocabulary/flyers.json`
- `tinysteps-data/vocabulary/ket.json`
- `tinysteps-data/vocabulary/pet.json`

---

## Các bước thực hiện

### Bước 1: Thu thập nguồn data
**Làm gì:** Clone repo CEFR-SP và tải Cambridge wordlists.
**Skill:** @git, @file-processing
**Chi tiết:**
1. Clone `github.com/yukiar/CEFR-SP` vào thư mục tạm
2. Đọc dataset, lọc ra các câu level A1, A2, B1
3. Trích xuất danh sách từ vựng xuất hiện trong các câu này (word frequency count)
4. Tải Cambridge wordlists cho Starters/Movers/Flyers/KET/PET (nếu có PDF, convert sang text)

**Output bước này:** File tạm `_raw/cefr_sp_words.json` và `_raw/cambridge_words.json`

**Validation:** Kiểm tra số lượng từ unique từ mỗi nguồn. Log ra console.

---

### Bước 2: Merge và phân loại
**Làm gì:** Kết hợp 2 nguồn, loại bỏ trùng lặp, phân loại theo level.
**Skill:** @json-processing
**Chi tiết:**
1. Lấy Cambridge wordlist làm PRIMARY — đây là nguồn chính thức
2. Bổ sung từ CEFR-SP nếu từ đó xuất hiện nhiều (frequency >= 3) mà Cambridge chưa có
3. Phân loại mỗi từ vào đúng 1 level dựa trên Cambridge level assignment
4. Nếu 1 từ xuất hiện ở nhiều levels trong Cambridge, giữ ở level THẤP nhất
5. Loại bỏ proper nouns, abbreviations, rất rare words

**Target số lượng:**
- Starters: ~300 từ
- Movers: ~400 từ (không trùng Starters)
- Flyers: ~500 từ (không trùng levels trước)
- KET: ~400 từ bổ sung
- PET: ~500 từ bổ sung

**Output bước này:** File tạm `_raw/classified_words.json`

**Validation:**
- Kiểm tra không có từ trùng giữa các levels
- Kiểm tra tổng số ~2100 từ
- Spot check 10 từ mỗi level — có đúng level không?

---

### Bước 3: Thêm metadata cho mỗi từ
**Làm gì:** Bổ sung IPA, part of speech, example sentence, image hint cho từng từ.
**Skill:** @english-linguistics, @json-processing
**Chi tiết:**
1. Với mỗi từ, thêm:
   - `ipa`: Phiên âm IPA (British English)
   - `pos`: Part of speech (noun/verb/adj/adv/prep/conj/pron/det/interjection/phrase)
   - `example_sentence`: Một câu ví dụ tự nhiên, **đúng level** (không dùng từ vượt level)
   - `image_hint`: Mô tả ngắn bằng English cho image generation (2-8 từ)
   - `topic_ids`: Tạm gán topic dựa trên semantic meaning (Agent 2 sẽ refine)
2. Với example_sentence: ưu tiên lấy từ CEFR-SP dataset (câu đã được chuyên gia validate). Nếu không có câu phù hợp, AI generate mới.
3. Với image_hint: mô tả cụ thể, có thể visualize. Tránh abstract ("a feeling of happiness" → sai. "a smiling person" → đúng).

**Lưu ý quan trọng:**
- Example sentence cho Starters: tối đa 5 từ, present tense only
- Example sentence cho Movers: tối đa 7 từ, có thể past simple
- Example sentence cho Flyers: tối đa 10 từ
- Example sentence cho KET: tối đa 12 từ
- Example sentence cho PET: tối đa 15 từ

**Output bước này:** File tạm `_raw/enriched_words.json`

**Validation:**
- Mỗi từ phải có đủ 7 required fields theo schema
- Spot check 5 example sentences mỗi level — câu có vượt level không?
- Spot check 5 image hints — có visualize được không?

---

### Bước 4: Gán ID và format output
**Làm gì:** Gán ID theo convention, format đúng schema, output 5 files JSON.
**Skill:** @json-processing
**Chi tiết:**
1. Gán ID format: `{level}_vocab_{3-digit-number}` (bắt đầu từ 001)
2. Sắp xếp từ theo alphabet trong mỗi level
3. Thêm `related_words` nếu có (synonyms, antonyms, same word family TRONG cùng level)
4. Thêm `frequency_rank` dựa trên word frequency data
5. Validate toàn bộ theo `schemas/vocabulary.schema.json`
6. Output 5 files vào `tinysteps-data/vocabulary/`

**Output cuối cùng:**
```
tinysteps-data/vocabulary/starters.json
tinysteps-data/vocabulary/movers.json
tinysteps-data/vocabulary/flyers.json
tinysteps-data/vocabulary/ket.json
tinysteps-data/vocabulary/pet.json
```

**Validation cuối:**
- [ ] Tất cả 5 files valid JSON
- [ ] Đúng schema (validate against vocabulary.schema.json)
- [ ] Tổng ~2100 từ (± 10%)
- [ ] Không duplicate IDs across files
- [ ] Không duplicate words across levels
- [ ] Mỗi từ có đủ required fields
- [ ] Log summary: {level}: {count} words

---

## Khi gặp vấn đề

| Vấn đề | Xử lý |
|--------|--------|
| Không tải được Cambridge PDF | Dùng CEFR-SP làm nguồn chính, bổ sung từ Oxford 3000/5000 wordlist (free) |
| Một từ khó xác định level | Gán vào level CAO hơn (an toàn hơn — không sợ quá khó ở level thấp) |
| Không tìm được example sentence đúng level | AI generate, nhưng phải validate lại rằng câu chỉ dùng từ trong level đó |
| Image hint khó mô tả (từ abstract) | Dùng tình huống thay vì vật thể. "happy" → "a teacher smiling at students" |

## Báo cáo khi hoàn thành

```
✅ Agent 1 (Vocabulary) hoàn thành
- Starters: {n} words
- Movers: {n} words
- Flyers: {n} words
- KET: {n} words
- PET: {n} words
- Tổng: {n} words
- Nguồn: Cambridge {x}%, CEFR-SP {y}%, AI generated {z}%
- Files: tinysteps-data/vocabulary/*.json
- Validation: PASSED / FAILED (chi tiết)
```
