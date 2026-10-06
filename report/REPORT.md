# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Phan Duy Bao | 2A202602767 | Cài đặt harness, chạy thí nghiệm, viết báo cáo |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: OpenAI, `LAB_MODEL=openai:gpt-6-luna`, `LAB_TEMPERATURE=1` (API trả 400 `Unsupported parameter: 'temperature'` khi đặt 0 nên không dùng được giá trị mặc định 0 của mẫu), `recursion_limit=60` (mặc định)
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21, Python 3.11.15, macOS (Darwin 25.5.0), chạy trực tiếp (không Docker)
- Số lần chạy tác vụ đã dùng / ngân sách: 9 lần chạy tác tử hoàn tất, đều trên tác vụ học (3 `baseline`, 3 `subagents`, 3 `skills-auto` trước đóng băng), 1 lần gọi curator, vài lần gọi thử rất nhỏ để kiểm tra mô hình; 1 lần chạy đánh giá (`baseline` trên `code-eval`) bị dừng giữa chừng theo yêu cầu, không tạo `run.json` và nhóm chưa thấy điểm nào của tác vụ đánh giá. Không đặt ngân sách cố định; dừng sớm để tiết kiệm token.
- Commit của tag `freeze`: `9bbee7f` (commit `hypotheses` là `284ad39`, đứng trước tag)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Trên tác vụ ĐÁNH GIÁ, `subagents` không hơn `baseline` về điểm (chênh điểm trung bình trong khoảng ±0,1, tức cỡ 1 check) nhưng tốn token gấp khoảng 3 đến 5 lần. Căn cứ: trên 3 tác vụ học, `subagents` cho đúng cùng điểm với `baseline` (7/10, 5/8, 6/9; check kỹ thuật 18/18 ở cả hai, check quy ước 0/9 ở cả hai) trong khi token trung bình tăng từ 38.922 lên 167.765 (4,3 lần); lỗi còn lại là quy ước không có trong đề, không phải thiếu khám phá hay thiếu rà soát mà subagent giải quyết; ở `data-learn` việc giao việc còn khẳng định 'no additional Acme reporting convention', củng cố việc bỏ sót. Phù hợp với ghi nhận chi phí đa tác tử cao của bài báo Anthropic về hệ thống nghiên cứu đa tác tử.
- H2 (skills-auto so với baseline): `skills-auto` đạt điểm trung bình cao nhất trên tác vụ đánh giá nhưng chỉ hơn `baseline` khoảng 0,05 đến 0,15 (1 đến 2 check mỗi tác vụ), và gần như toàn bộ phần tăng đến từ các quy ước đã xuất hiện trong phản hồi của tác vụ học; quy ước mới chỉ có ở tác vụ đánh giá sẽ không được skill giúp. Căn cứ: ở Phần 3.4 trên tác vụ học, check quy ước tăng từ 0/9 lên 3/9 (điểm học trung bình 0,66 lên 0,77); skill đã đọc 3/3 lần chạy nhưng skill dùng cụm 'when required' nên tác tử làm theo đề thay vì skill khi đề không nêu quy ước (`data-learn` vẫn 5/8). Phù hợp với SkillsBench (skill do mô hình tự sinh trung bình không có lợi hoặc lợi nhỏ).
- H3 (tác vụ học so với tác vụ đánh giá): Mức tăng của `skills-auto` so với `baseline` trên tác vụ đánh giá sẽ nhỏ hơn mức tăng trên tác vụ học (+0,11), tức là có quá khớp/không chuyển giao hoàn toàn; điểm `baseline` trên tác vụ đánh giá dự kiến khoảng 0,6 đến 0,7 vì check kỹ thuật vẫn đạt còn check quy ước trượt. Căn cứ: skill sinh ra bám sát từng quy tắc của phản hồi tác vụ học (đổi tên dịch vụ, sắp xếp, type hint, số cent) và README nêu tác vụ đánh giá thêm một quy ước mới; SkillEvolBench ghi nhận lợi ích trên tác vụ học thường không chuyển sang tác vụ mới. Với n=3 tác vụ mỗi vai trò và nhiệt độ 1, chênh lệch dưới 0,1 chưa đủ để kết luận.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Công cụ mặc định: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep` (tệp), `execute` (shell) và `task` (giao việc cho subagent). Chỉ `execute` cho phép chạy lệnh.
2. Mô tả của `task` nói `general-purpose` là subagent "for researching complex questions, searching for files and content, and executing multi-step tasks" và "has access to all tools as the main agent". Mỗi lần gọi là "stateless by default: the agent sees only the prompt you give it and returns a single final report", nên nó không thấy hội thoại của tác tử chính, chỉ thấy prompt được giao.
3. Từ `task`: "Put full detail in the prompt and state exactly what it should return". Từ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail." System prompt mặc định là chuỗi rỗng (`''`), nên hành vi được định hướng gần như hoàn toàn bởi mô tả công cụ.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `rule_type_hints` | E | `detail`: 'RULE: every public function ... has type annotations on all parameters and on the return value.' Cùng check đạt ở 3.4 sau khi skill được đọc. |
| code-learn | `rule_regression_tests` | E | 'RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3)'. Vết baseline: không tạo tệp test mới; tên tệp và số lượng không có trong đề. |
| code-learn | `rule_changelog` | E | 'RULE: record each fix in CHANGELOG.md under the heading ## Unreleased as a bullet - fix(<function name>) ...'. Vết baseline: `CHANGELOG.md` chỉ hiện trong kết quả `glob`, không có lệnh `read_file` nào đọc nó. |
| data-learn | `rule_money_in_cents` | E | 'RULE: money values in answer.json are integer cents'. Vết: `write_file` ghi `"north_q1_revenue": 3130.24` (USD) theo đề ghi 'number'. |
| data-learn | `rule_meta_block` | E | 'RULE: answer.json has an object `meta` = {source, rows_in, rows_used}'. Vết: answer.json chỉ có 5 khóa theo đề. |
| data-learn | `rule_clean_csv` | E | 'RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents'. Vết: không có lệnh ghi `clean.csv`. |
| logs-learn | `rule_service_names` | E | 'RULE: service names ... lower-case with - replaced by _ (payment-service -> payment_service)'. |
| logs-learn | `rule_sorted_errors` | E | 'RULE: `errors` is sorted by service, then by timestamp_utc, ascending.' |
| logs-learn | `rule_schema_header` | E | 'RULE: the top-level object has schema_version: 2 and generated_by: log-triage.' |

Nhận xét: nhóm E chiếm 9/9 check thất bại của `baseline` (lần chạy đầu tiên; số liệu từ `results/baseline/*/run.json`). Bằng chứng phủ định cho nhóm A đến D: `python scripts/check_breakdown.py` cho `baseline` check kỹ thuật 18/18 đạt, check quy ước 0/9 đạt (đúng bằng với `subagents`: 18/18 và 0/9). Nhóm F: không thấy; ở `data-learn` và `logs-learn` tệp đầu ra mà câu trả lời cuối nói đã tạo đều có thật vì các check kỹ thuật đọc chúng và đạt, ở `code-learn` các tệp được nêu đều là tệp đã sửa. Không có lỗi hạ tầng (cột `error` đều `None`). Skill phòng ngừa được nhóm E ở mức giới hạn: quy ước chỉ học được từ phản hồi của bot (không có trong đề hay workspace), nên skill chỉ giúp khi nó ghi lại được nội dung quy tắc cụ thể; ví dụ `CHANGELOG.md` trong workspace chỉ có tiêu đề `## Unreleased` rỗng nên đọc nó không cho biết định dạng bullet.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế): ba subagent trong `src/lab/subagents.py`.
  - `explorer` (chỉ đọc): đọc README, docstring, mẫu dữ liệu và báo cáo sự thật cùng quy tắc; dùng trước khi sửa. Nhắm vào nhóm lỗi A (bỏ qua đặc tả) và D (bỏ sót dữ liệu bẩn).
  - `implementer`: thực hiện thay đổi, chạy test hoặc script, báo cáo kết quả thật; sửa nguyên nhân gốc (nhóm C). Chỉ nên nhận đề đủ quy tắc, vì nó không thấy ngữ cảnh của tác tử chính.
  - `reviewer` (chỉ đọc): đối chiếu độc lập kết quả với từng yêu cầu, báo OK hoặc VIOLATED; nhắm vào nhóm B (không kiểm chứng) và F (báo cáo sai sự thật).
  - Mỗi `description` viết như chỉ dẫn hành động (khi nào gọi). `PATHS_NOTE` được `build_agent` nối vào `system_prompt` của từng subagent.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0): `code-learn` 3 (explorer, implementer, reviewer), `data-learn` 2 (explorer, implementer), `logs-learn` 2 (explorer, implementer); `baseline` đều 0. Tác tử chính giao việc ở cả 3 tác vụ và theo đúng thứ tự khám phá, thực hiện, rà soát (chỉ `code-learn` gọi reviewer). Điểm không đổi so với `baseline`: 7/10, 5/8, 6/9.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): lời giao việc nêu đủ quy tắc của đề và đường dẫn (ví dụ `logs-learn`: UTC, `repeat_count`, chỉ ERROR/CRITICAL, chỉ sửa `workspace/errors.json`), và báo cáo của subagent có được kiểm tra: ở `logs-learn` tác tử chính viết cho implementer 'prior report had inaccurate total counts' và yêu cầu tự tính lại. Mặt thiếu: vì quy ước Acme nằm ngoài đề nên không subagent nào biết; ở `data-learn`, sau khi explorer không tìm thấy quy ước, tác tử chính ghi vào lời giao việc 'No additional Acme reporting convention appears ... so output only the requested five keys', tức giao việc làm cố định luôn việc bỏ sót. Reviewer ở `code-learn` chỉ được yêu cầu kiểm tra docstring và 'idiomatic conventions' nên không bắt được 3 check quy ước.
- Ảnh hưởng đến token và thời gian: token `subagents` so với `baseline`: `code-learn` 177.000 so với 65.798 (2,7 lần), `data-learn` 80.067 so với 25.662 (3,1 lần), `logs-learn` 246.228 so với 25.306 (9,7 lần); trung bình 167.765 so với 38.922 (4,3 lần). Thời gian: 147,2 s, 56,2 s, 155,1 s so với 45,9 s, 19,2 s, 21,1 s. Không có lợi ích về điểm đi kèm trên tác vụ học.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: 1 lần chạy (`python -m lab.curator` trên kết quả `baseline` của tác vụ học), sinh 3 skill hợp lệ; xóa 0 skill, không chạy lại (không có skill sai hoặc có hại, và để tiết kiệm token). Không sửa tay.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `repo-maintenance-quality-gates` | Chung chung ở câu chữ nhưng 3 trong 5 bước là 3 quy tắc `rule_` của `code-learn` (type hint, test hồi quy, changelog); không chứa tên tệp hay hàm của tác vụ. | Không sai. Mơ hồ: nói 'meet any stated test-file ... requirements' và 'the prescribed bullet format' nhưng không nêu tên `tests/test_regressions.py`, tiêu đề, hay định dạng bullet nên tác tử tự đặt: thêm 1 bullet không theo `- fix(<hàm>):` và test vào `tests/test_edge_cases.py` (cả 2 check vẫn trượt). Bước type hint đúng và hiệu quả: `rule_type_hints` đạt. | 9 dòng; `description` 'Use when fixing bugs or maintaining a Python package under repository-level quality checks' (tốt, đủ rộng). `skills_read`: được đọc ở `code-learn` và (không liên quan) ở `data-learn`. `code-learn` 7/10 lên 8/10. |
| `structured-log-exports` | Một nửa tổng quát (bước kiểm tra schema, chuẩn hóa múi giờ, đếm), một nửa là quy ước của `logs-learn` (đổi dấu gạch ngang thành gạch dưới, sắp xếp theo service rồi thời gian). | Đúng với phản hồi: `rule_service_names` và `rule_sorted_errors` đạt ở 3.4. Thiếu nội dung quy tắc cuối: nói 'preserve all required top-level fields' nhưng không nêu `schema_version`/`generated_by` nên `rule_schema_header` vẫn trượt. Cụm 'when required' làm yếu mệnh lệnh. | 9 dòng; `description` 'Use when parsing logs into structured JSON summaries or error records' (đủ rộng cho họ logs). `skills_read`: đọc ở `logs-learn`. `logs-learn` 6/9 lên 8/9. |
| `tabular-data-contracts` | Tổng quát nhất về quy trình (đếm dòng trước khi khử trùng, theo dõi giá trị thiếu, chuẩn hóa múi giờ, kiểm tra đầu ra) và có ghi quy ước 'integer cents'; không chứa tên cột hay tệp. | Nội dung không sai nhưng có điều kiện: 'use integer cents when the contract requires cents', trong khi đề không nêu 'contract'. Vết `data-learn`: tác tử đọc skill rồi vẫn `write_file` 5 khóa với `3130.24` (USD) và không ghi `meta` hay `clean.csv`, làm theo chữ 'number' của đề. Kết quả `data-learn` không đổi 5/8. | 10 dòng; `description` 'Use when cleaning, deduplicating, analyzing, or exporting tabular data to specified output files' (rộng, đúng tình huống). `skills_read`: đọc ở `data-learn` và `logs-learn`. Không giúp thêm check nào. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

**Phạm vi dữ liệu: chỉ có tác vụ học.** Tác vụ đánh giá và lần chạy chính thức `skills-auto` sau đóng băng chưa được chạy (xem mục 9), nên cột `skills-auto` không xuất hiện trong `report/table.md` và hàng 'evaluation tasks' để trống. `python scripts/verify_freeze.py` báo `checked 0 runs of skill conditions: OK`: kết quả OK này chỉ có nghĩa là commit `hypotheses` (đã điền H1 đến H3) đứng trước tag `freeze` và `skills/` không đổi, vì không có lần chạy `skills-auto` nào để đối chiếu.

Kết quả `python -m lab.compare` (nội dung `report/table.md`):

```text
| Task | baseline | subagents |
|---|---|---|
| code-learn | 7/10 | 7/10 |
| data-learn | 5/8 | 5/8 |
| logs-learn | 6/9 | 6/9 |
| **Mean score - learning tasks** | 0.66 | 0.66 |
| **Mean score - evaluation tasks** | - | - |
| **Mean tokens per run** | 38,922 | 167,765 |
| **Runs that read a skill** | 0/3 | 0/3 |
```

Kết quả `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      learn    18/18         0/9           38,922      0/3     
subagents     learn    18/18         0/9          167,765      0/3
```

Kết quả `skills-auto` ở Phần 3.4 (chạy TRƯỚC khi đóng băng, đã chuyển sang `results/skills-auto-dev/` nên `lab.compare` không đọc), dùng cùng bộ skill 3 skill như lúc đóng băng, tính từ các `run.json`:

```text
| Task | baseline | subagents | skills-auto (dev, trước đóng băng) |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 8/10 |
| data-learn | 5/8 | 5/8 | 5/8 |
| logs-learn | 6/9 | 6/9 | 8/9 |
| **Điểm trung bình tác vụ học** | 0.66 | 0.66 | 0.77 |
| **Check kỹ thuật đạt** | 18/18 | 18/18 | 18/18 |
| **Check quy ước (`rule_`) đạt** | 0/9 | 0/9 | 3/9 |
| **Token trung bình mỗi lần chạy** | 38,922 | 167,765 | 59,850 |
| **Lần chạy có đọc skill** | 0/3 | 0/3 | 3/3 |
| **Điểm trên 1.000 token** | 0.0171 | 0.0040 | 0.0129 |
```

Không có lần chạy nào có `error`; `skills_modified` là `false` ở mọi lần chạy `skills-auto-dev`. Điểm trên 1.000 token = điểm trung bình chia cho token trung bình (nghìn).

## 8. Phân tích

Mọi số liệu dưới đây là của 3 tác vụ học (mỗi cấu hình chạy một lần). Tác vụ đánh giá chưa được chạy, nên các phần cần dữ liệu đánh giá được ghi rõ là không có dữ liệu, và H1 đến H3 (đã commit trước tag) chưa được kiểm chứng.

1. Điểm tác vụ học: `baseline` 0.66, `subagents` 0.66 (đúng bằng `baseline` ở cả 3 tác vụ), `skills-auto` 0.77 (trước đóng băng, +0.11). Tác vụ đánh giá: không có dữ liệu, nên chưa thể nói có điều kiện nào cải thiện tác vụ học mà không chuyển sang tác vụ đánh giá (dấu hiệu quá khớp); chỉ có thể nói cải thiện của `skills-auto` mới được đo trên chính tập mà curator đã học phản hồi.
2. Check kỹ thuật đạt 18/18 ở `baseline`, 18/18 ở `subagents` và 18/18 ở `skills-auto`, nên skill không có gì để giúp ở nhóm này. Check quy ước (`rule_`): 0/9, 0/9 và 3/9. Skill giúp 3 check: `rule_type_hints` (`code-learn`), `rule_service_names` và `rule_sorted_errors` (`logs-learn`). Check quy ước mới của tác vụ đánh giá: không có dữ liệu; theo mục 6, skill chỉ ghi lại các quy tắc đã thấy trong phản hồi của tác vụ học nên không có nội dung nào dành cho một quy ước chưa từng thấy.
3. Skill giúp: `rule_service_names` ở `logs-learn`: `skills_read` = 2, skill `structured-log-exports` được đọc và có bước 'normalize service names to lowercase and replace hyphens with underscores', câu trả lời cuối nói 'Service names are normalized and records are sorted by service and timestamp', check đạt. Skill không giúp: `rule_money_in_cents` ở `data-learn`: skill `tabular-data-contracts` được đọc (bước 'use integer cents when the contract requires cents') nhưng vết cho thấy `write_file` vẫn ghi `"north_q1_revenue": 3130.24` và chỉ 5 khóa, tức đọc nhưng làm theo chữ 'number' của đề vì điều kiện 'when the contract requires' không được thỏa. Ngoài ra `rule_changelog` và `rule_regression_tests` trượt vì skill nói 'prescribed bullet format' và 'stated test-file requirements' mà không nêu định dạng, tác tử tự đặt (1 bullet không theo `- fix(<hàm>):`, test vào `tests/test_edge_cases.py`), và `rule_schema_header` trượt vì skill không nêu giá trị `schema_version`/`generated_by`. Skill thiếu hoặc mơ hồ là nguyên nhân chính, không phải việc skill không được đọc (đọc 3/3 lần chạy).
4. Chi phí (tác vụ học): token trung bình `baseline` 38,922, `subagents` 167,765 (4.3 lần), `skills-auto` 59,850 (1.5 lần). Điểm trên 1.000 token: 0.0171, 0.0040, 0.0129, tức `baseline` hiệu quả nhất theo chỉ số này, `skills-auto` đứng sau, `subagents` thấp nhất. Trên tập học, đa tác tử không đáng chi phí: cùng điểm với `baseline` nhưng tốn 4.3 lần token. Chi phí cao hơn của `skills-auto` đến từ việc đọc skill (thêm lượt gọi công cụ) và tác tử làm thêm việc (ví dụ thêm test, sửa changelog).
5. Rò rỉ dữ liệu: không thấy. Curator chỉ đọc các lần chạy có `role == "learn"` của `baseline`; `validate_skill` loại skill chứa định danh của tác vụ đánh giá (cả 3 skill đều qua); nhóm không sửa tay skill và chưa mở tệp của tác vụ đánh giá. Quá khớp: có nguy cơ về cấu trúc, vì mọi quy tắc cụ thể trong skill (số cent, đổi gạch ngang thành gạch dưới, sắp xếp theo dịch vụ rồi thời gian, type hint) lấy nguyên từ phản hồi của tác vụ học; việc nó chuyển được sang tác vụ đánh giá hay không thì chưa được đo.
6. Nhiễu: không đo được. Cần so điểm Phần 3.4 với điểm sau đóng băng của cùng bộ skill, nhưng lần chạy sau đóng băng chưa được thực hiện. Dữ liệu duy nhất liên quan: `baseline` và `subagents` cho điểm giống hệt nhau ở cả 3 tác vụ (và cùng 9 check quy ước trượt), cho thấy kết quả trên tập học khá ổn định giữa hai cấu hình rất khác nhau, nhưng đây là hai điều kiện khác nhau chứ không phải chạy lặp, nên không thay được ước lượng nhiễu. Với `LAB_TEMPERATURE=1` và một lần chạy mỗi ô, chênh lệch một check (0,1 điểm tác vụ) cần được đọc là nằm trong khả năng nhiễu.

## 9. Hạn chế và tính hợp lệ

1. **Chưa chạy tác vụ đánh giá** (dừng theo quyết định tiết kiệm token). Ảnh hưởng lớn nhất: H1 đến H3 chưa được kiểm chứng, không có số liệu để kết luận về tổng quát hóa, quá khớp hay hiệu quả của quy ước mới; mọi nhận định về `skills-auto` chỉ áp dụng cho tập học mà curator đã nhìn thấy phản hồi. Ngoài ra không có lần chạy chính thức `skills-auto` sau đóng băng nên `verify_freeze.py` chỉ xác nhận thứ tự commit, tag và `skills/`, không xác nhận được việc các lần chạy dùng đúng skill đã đóng băng.
2. **Số mẫu rất nhỏ và một lần chạy mỗi ô**: 3 tác vụ học, mỗi cấu hình một lần. Một check chênh lệch bằng khoảng 0,1 điểm tác vụ, nên chênh lệch `skills-auto` +0,11 so với `baseline` tương đương 3 check trên 27 (18 lên 21 check đạt), chưa đủ để loại trừ nhiễu.
3. **`temperature` buộc phải bằng 1** (API từ chối 0) và nhiễu chưa được đo (không có lần chạy lặp): kết quả có thể thay đổi giữa các lần chạy, làm yếu mọi so sánh ở mức một check.
4. **Một mô hình duy nhất** (`openai:gpt-6-luna`): kết luận về việc tác tử làm theo đề hơn skill, hay về mức token của subagent, có thể không đúng với mô hình khác. Vết chứa khối reasoning đã mã hóa nên lý do ra quyết định của tác tử chỉ suy ra được từ các lệnh gọi công cụ.
5. **Tác vụ do giảng viên thiết kế với quy ước có sẵn**: phần lớn lỗi là quy ước không có trong đề, nên cải thiện của skill chủ yếu là 'nhớ lại quy ước đã thấy trong phản hồi' chứ không phải năng lực tổng quát; điều này làm kết quả `skills-auto` trên tập học có vẻ tốt hơn mức chuyển giao thực tế.
6. **Curator chỉ chạy một lần** và có tính ngẫu nhiên: bộ 3 skill có thể khác ở lần chạy khác; không có so sánh giữa các lần.

## 10. Kết luận

Trên 3 tác vụ học, cả 9 check thất bại của `baseline` đều là quy ước tổ chức không có trong đề, còn check kỹ thuật đạt 18/18 ở cả ba điều kiện. `subagents` cho điểm bằng `baseline` (0,66) nhưng tốn 4,3 lần token nên không đáng chi phí trên tập này. Skill do curator sinh nâng check quy ước từ 0/9 lên 3/9 (điểm học 0,66 lên 0,77, một lần chạy, trước đóng băng), nhưng cụm điều kiện 'when required' khiến tác tử làm theo đề thay vì skill khi đề không nêu quy ước. Vì tác vụ đánh giá chưa được chạy, chưa thể kết luận về tổng quát hóa hay quá khớp và H1 đến H3 chưa được kiểm chứng. Đề xuất: sửa prompt của curator để viết quy tắc cụ thể, không điều kiện (nêu tên khóa, tên tệp, định dạng mà phản hồi đã phát biểu), rồi chạy tác vụ đánh giá sau tag `freeze` ít nhất 2 lần mỗi cấu hình để đo nhiễu.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `/opt/homebrew/bin/python3.11 -m venv .venv && source .venv/bin/activate && pip install -e .`; `cp .env.example .env`; `mkdir -p report && cp REPORT_TEMPLATE.md report/REPORT.md`; `pytest tests/test_01_provided.py` (15 passed).
  2. Cài đặt `subagents.py`, `agent.py`, `runner.py`, `curator.py`; `pytest` (32 passed: 15 + 9 + 6 + 2); `python scripts/tour.py`.
  3. `python -m lab.runner --condition baseline --tasks data-learn`; `python -m lab.runner --condition baseline --tasks code-learn logs-learn`; `python -m lab.runner --condition subagents --tasks learn`.
  4. `python -m lab.curator` (1 lần); `python -m lab.runner --condition skills-auto --tasks learn`.
  5. `mv results/skills-auto results/skills-auto-dev`; commit `hypotheses`; `git commit --allow-empty -m "freeze skills" && git tag freeze`; `python scripts/verify_freeze.py` (OK, 0 lần chạy được kiểm tra).
  6. `python -m lab.runner --condition baseline --tasks eval` (bắt đầu rồi bị dừng trước khi xong tác vụ đầu tiên, theo yêu cầu; không có kết quả được lưu); các lệnh `--condition subagents --tasks eval` và `--condition skills-auto --tasks all` chưa được chạy.
  7. `python -m lab.compare > report/table.md`; `python scripts/check_breakdown.py`; `python scripts/verify_freeze.py`.
- Thử thách mở rộng (nếu có): không thực hiện.
- Ghi chú khác: (a) `final_message` trong `run.json` lưu nguyên danh sách khối nội dung của mô hình (kể cả khối reasoning mã hóa) nên một số `run.json` dài; điểm, token và các số đếm không bị ảnh hưởng. (b) `results/skills-auto-dev/` là bản sao lưu Phần 3.4 theo GUIDE 4.2; `lab.compare` bỏ qua thư mục này. (c) Để chạy tiếp tác vụ đánh giá một cách hợp lệ: giữ nguyên `skills/` và tag `freeze`, chạy các lệnh ở mục 6 trên, rồi `python scripts/verify_freeze.py` và `python -m lab.compare > report/table.md`.
