# TC2 - Tổng kết theo MVP / Research / Evaluate

Ngày: 18/09/2026. Bám theo đúng 3 mục mentor giao trong đề bài TC2 (mutation testing pilot). Chi tiết đầy đủ nằm trong
[`README.md`](../README.md), [`docs/review-baseline.md`](review-baseline.md) và [`docs/comparisons/`](comparisons/).

## MVP

Đã mutate 2 module nghiệp vụ (vượt yêu cầu tối thiểu "pilot một project"), phạm vi giới hạn đúng phần quy tắc nghiệp vụ,
không mutate dữ liệu hay code ngoài phạm vi:

| Target | Công cụ | Phạm vi mutate |
| --- | --- | --- |
| Dinero.js (TypeScript) | StrykerJS + Vitest | Phép tính, so sánh, đổi scale, làm tròn, chia tiền theo tỉ lệ (`core/api`, `core/utils`, `core/divide`) |
| Stateless (C#) | Stryker.NET + xUnit | Quy tắc chuyển trạng thái: guard, trigger bị bỏ qua, reentry (`src/Stateless`) |

Quy trình: chạy baseline → review tay toàn bộ mutant sống sót → viết test cho các trường hợp mentor xác nhận là lỗ hổng
thật (`real_gap`) → chạy lại chính thức với nhãn `after-tests`.

**Kết quả:** mentor đã xác nhận toàn bộ 12 mutant `real_gap` (7 Dinero.js + 5 Stateless, xem `data/reviewed/*.csv`,
`mentor_confirmed = yes`). 13 test mới (9 Dinero.js trong 4 file, 4 Stateless) đặt trong `patches/`, bắt được **đúng
12/12** lỗ hổng đã xác nhận khi chạy `after-tests`.

## Research

**Câu hỏi:** test nào chạy qua code nhưng không phát hiện được thay đổi hành vi?

Tìm được 3 kiểu test yếu cụ thể, mỗi kiểu có ví dụ mutant thật (chi tiết trong `docs/review-baseline.md`):

1. **Assertion chỉ kiểm tra kiểu exception** (Stateless, mutant 1579): hai lỗi khác nhau ném cùng một loại exception,
   test không phân biệt được lỗi nào xảy ra.
2. **Test bị một điều kiện khác "che"** (Dinero.js `allocate`, mutant 24/31/32): input tỉ lệ âm dùng trong test đã bị
   một điều kiện khác chặn từ trước, nên điều kiện cần kiểm tra chưa bao giờ thực sự quyết định kết quả.
3. **Test có tên đúng nhưng input không đi vào nhánh cần kiểm tra** (Dinero.js `distribute`, mutant 297/298): tên test
   nói "không bị treo", nhưng input dùng để test lại chia đều nên vòng lặp không chạy lần nào.

**Hạn chế phát hiện thêm:** property test dùng fast-check (Dinero.js) không cố định seed, nên một mutant (81) lúc bị bắt
lúc không giữa các lần chạy giống hệt nhau về code và cấu hình. Phải dùng lần chạy lặp lại làm mốc so sánh thay vì tin
một lần chạy baseline duy nhất.

**Phát hiện phụ ngoài phạm vi câu hỏi nghiên cứu:** `distribute(1e32, [1, 1, 1])` trong Dinero.js bị treo thật (phần dư
rơi đúng 2^53 khiến nhánh chống vòng lặp vô hạn không kích hoạt). Chưa báo lên upstream, đang chờ quyết định có nên báo
hay không.

## Evaluate

Điểm luôn kèm mẫu số; Equivalent, invalid (CompileError/RuntimeError) và Timeout báo tách riêng, không gộp vào điểm
mutation score chính.

| Target | Lần chạy | Điểm (bắt được / hợp lệ) | Killed | Timeout | Survived | NoCoverage | Không hợp lệ | Thời gian |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dinero.js | baseline | 348/359 = 96.9% | 344 | 4 | 10 | 1 | 0 | 101 s |
| Dinero.js | baseline lặp lại | 347/359 = 96.7% | 343 | 4 | 11 | 1 | 0 | 114-118 s |
| Dinero.js | **after-tests** | **354/359 = 98.6%** | 348 | 6 | 5 | 0 | 0 | 70-119 s |
| Stateless | baseline | 85/97 = 87.6% | 85 | 0 | 6 | 6 | 20 | 38 s |
| Stateless | **after-tests** | **90/97 = 92.8%** | 90 | 0 | 4 | 3 | 20 | 34-43 s |

Sau khi loại các mutant đã xác nhận `equivalent` khỏi mẫu số: Dinero.js 354/355 = 99.7%, Stateless 90/95 = 94.7%.

**Survivor đáng xử lý (đã mentor xác nhận):**

| Target | real_gap | equivalent | not_worth | Lỗ hổng thật bị test mới bắt |
| --- | ---: | ---: | ---: | ---: |
| Dinero.js | 7 | 4 | 1 | 7/7 |
| Stateless | 5 | 2 | 5 | 5/5 |

Bảng so sánh mutant-theo-mutant (trước/sau, ghép theo vị trí + mutator, không theo id) nằm trong
[`dinero-repeat1-vs-after-tests.md`](comparisons/dinero-repeat1-vs-after-tests.md) và
[`stateless-baseline-vs-after-tests.md`](comparisons/stateless-baseline-vs-after-tests.md).

## Trạng thái

MVP, Research và Evaluate theo đúng đề bài đã hoàn thành và được mentor xác nhận. Việc còn mở duy nhất: quyết định có
báo bug `distribute` lên upstream Dinero.js hay không.
