# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Phan Duy Bao | 2A202602767 | Cài đặt harness, chạy thí nghiệm, viết báo cáo |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: OpenAI, `LAB_MODEL=openai:gpt-6-luna`, `LAB_TEMPERATURE=1` (API trả 400 `Unsupported parameter: 'temperature'` khi đặt 0 nên không dùng được giá trị mặc định 0 của mẫu), `recursion_limit=60` (mặc định)
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21, Python 3.11.15, macOS (Darwin 25.5.0), chạy trực tiếp (không Docker)
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Trên tác vụ ĐÁNH GIÁ, `subagents` không hơn `baseline` về điểm (chênh điểm trung bình trong khoảng ±0,1, tức cỡ 1 check) nhưng tốn token gấp khoảng 3 đến 5 lần. Căn cứ: trên 3 tác vụ học, `subagents` cho đúng cùng điểm với `baseline` (7/10, 5/8, 6/9; check kỹ thuật 18/18 ở cả hai, check quy ước 0/9 ở cả hai) trong khi token trung bình tăng từ 38.922 lên 167.765 (4,3 lần); lỗi còn lại là quy ước không có trong đề, không phải thiếu khám phá hay thiếu rà soát mà subagent giải quyết; ở `data-learn` việc giao việc còn khẳng định 'no additional Acme reporting convention', củng cố việc bỏ sót. Phù hợp với ghi nhận chi phí đa tác tử cao của bài báo Anthropic về hệ thống nghiên cứu đa tác tử.
- H2 (skills-auto so với baseline): `skills-auto` đạt điểm trung bình cao nhất trên tác vụ đánh giá nhưng chỉ hơn `baseline` khoảng 0,05 đến 0,15 (1 đến 2 check mỗi tác vụ), và gần như toàn bộ phần tăng đến từ các quy ước đã xuất hiện trong phản hồi của tác vụ học; quy ước mới chỉ có ở tác vụ đánh giá sẽ không được skill giúp. Căn cứ: ở Phần 3.4 trên tác vụ học, check quy ước tăng từ 0/9 lên 3/9 (điểm học trung bình 0,66 lên 0,77); skill đã đọc 3/3 lần chạy nhưng skill dùng cụm 'when required' nên tác tử làm theo đề thay vì skill khi đề không nêu quy ước (`data-learn` vẫn 5/8). Phù hợp với SkillsBench (skill do mô hình tự sinh trung bình không có lợi hoặc lợi nhỏ).
- H3 (tác vụ học so với tác vụ đánh giá): Mức tăng của `skills-auto` so với `baseline` trên tác vụ đánh giá sẽ nhỏ hơn mức tăng trên tác vụ học (+0,11), tức là có quá khớp/không chuyển giao hoàn toàn; điểm `baseline` trên tác vụ đánh giá dự kiến khoảng 0,6 đến 0,7 vì check kỹ thuật vẫn đạt còn check quy ước trượt. Căn cứ: skill sinh ra bám sát từng quy tắc của phản hồi tác vụ học (đổi tên dịch vụ, sắp xếp, type hint, số cent) và README nêu tác vụ đánh giá thêm một quy ước mới; SkillEvolBench ghi nhận lợi ích trên tác vụ học thường không chuyển sang tác vụ mới. Với n=3 tác vụ mỗi vai trò và nhiệt độ 1, chênh lệch dưới 0,1 chưa đủ để kết luận.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Công cụ mặc định: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep` (tệp), `execute` (shell) và `task` (giao việc cho subagent). Chỉ `execute` cho phép chạy lệnh.
2. Mô tả của `task` nói `general-purpose` là subagent "for researching complex questions, searching for files and content, and executing multi-step tasks" và "has access to all tools as the main agent". Mỗi lần gọi là "stateless by default: the agent sees only the prompt you give it and returns a single final report", nên nó không thấy hội thoại của tác tử chính, chỉ thấy prompt được giao.
3. Từ `task`: "Put full detail in the prompt and state exactly what it should return". Từ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail." System prompt mặc định là chuỗi rỗng (`''`), nên hành vi được định hướng gần như hoàn toàn bởi mô tả công cụ.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

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

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
