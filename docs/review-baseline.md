# Review mutant sống sót sau baseline (đã được mentor xác nhận)

Ngày đề xuất: 17/09/2026. Ngày mentor xác nhận: 18/09/2026. Mọi verdict dưới đây ban đầu là **đề xuất của Claude**; mentor đã
xác nhận đồng ý toàn bộ (`mentor_confirmed = yes` trong cả hai file CSV). Dữ liệu chi tiết nằm trong
[`data/reviewed/dinero.csv`](../data/reviewed/dinero.csv) và [`data/reviewed/stateless.csv`](../data/reviewed/stateless.csv).

Test ứng viên trong [`patches/`](../patches/) đã trở thành chính thức và được chạy lại với nhãn `after-tests`
(xem [Kết quả chạy chính thức](#kết-quả-chạy-chính-thức-after-tests) bên dưới). Chúng chỉ được thêm tạm vào repo mục tiêu
khi chạy `tc2 run --with-tests`.

## Tổng quan

| Target | Mutant cần review | real_gap | equivalent | not_worth |
| --- | ---: | ---: | ---: | ---: |
| Dinero.js | 12 (11 từ baseline + 1 phát hiện do seed ngẫu nhiên) | 7 | 4 | 1 |
| Stateless | 12 | 5 | 2 | 5 |

## Dinero.js

| Mutant | Chỗ sửa | Verdict | Lý do ngắn |
| --- | --- | --- | --- |
| 24, 31, 32 | `allocate.ts:80,87`: bỏ hoặc nới kiểm tra "không có tỉ lệ âm" | real_gap | Test tỉ lệ âm hiện có dùng `[-50, -50]`, vốn đã bị chặn bởi điều kiện "có ít nhất một tỉ lệ dương". Chưa có test cho trường hợp trộn như `[-50, 150]`. |
| 78 | `haveSameAmount.ts:26`: `every` thành `some` | real_gap | Mọi test chỉ so 2 object nên `every` và `some` cho cùng kết quả. |
| 81 | `haveSameCurrency.ts:14`: `every` thành `some` | real_gap | Giống mutant 78. Baseline bắt được mutant này **chỉ nhờ may mắn**: một property test của fast-check chạy với seed ngẫu nhiên tình cờ tìm ra phản ví dụ. |
| 297, 298 | `distribute.ts:68`: nhánh chống vòng lặp vô hạn | real_gap | Test `does not hang with amounts larger than MAX_SAFE_INTEGER` chia đều nên **vòng lặp chạy 0 lần**, và nhánh chống treo chưa bao giờ được kiểm tra. `distribute(1e33, [1, 1, 1])` thì có đi vào nhánh này. |
| 201, 202 | `trimScale.ts:28`: bỏ nhánh trả về sớm | equivalent | Vẫn gọi `transformScale` với cùng scale nên giá trị trả về bằng nhau, chỉ khác tham chiếu object. |
| 285 | `distribute.ts:51`: bỏ bước lọc tỉ lệ 0 | equivalent | Phần dư luôn nhỏ hơn số tỉ lệ khác 0, nên các vị trí có tỉ lệ 0 không bao giờ được cộng. Kiểm tra trên 200.000 input ngẫu nhiên: 0 khác biệt. |
| 311 | `getAmountAndScale.ts:10`: `value?.scale` thành `value.scale` | equivalent | Trong nhánh này `value` chắc chắn là object. |
| 336 | `isScaledAmount.ts:6`: bỏ `?.` | not_worth | Chỉ khác khi tỉ lệ là `null`/`undefined`, mà kiểu TypeScript không cho phép. |

### Bug phát hiện thêm (chưa báo lên upstream)

`distribute(1e32, [1, 1, 1])` với calculator kiểu `number` **bị treo**:
- Sau khi chia, phần dư bằng đúng 2^53. Tại giá trị này phép trừ 1 vẫn có tác dụng, nên nhánh chống treo (`newRemainder === remainder`) không kích hoạt, và vòng lặp phải chạy khoảng 9·10^15 lần.
- Đã kiểm tra trên code thật: sau 60 giây vẫn chưa xong, trong khi ca đối chứng `1e20` xong trong 2 giây.
- Bug này không có trong test ứng viên, vì một test bị treo sẽ làm treo cả bộ test.
- Nên hỏi mentor có muốn báo lên repo Dinero.js không.

## Stateless

| Mutant | Chỗ sửa | Verdict | Lý do ngắn |
| --- | --- | --- | --- |
| 1579 | `StateRepresentation.cs:95`: bỏ `throw` "Multiple permitted exit transitions" | real_gap | Test `ExceptionWhenPermitIfHasMultipleNonExclusiveGuards` chỉ kiểm tra kiểu exception. Nhánh "trigger không được xử lý" cũng ném `InvalidOperationException`, nên test không phân biệt được hai lỗi. **Đây là ví dụ rõ nhất của assertion yếu.** |
| 1635, 1636 | `StateRepresentation.cs:205-206`: thoát superstate trung gian | real_gap | Chưa có test cho việc chuyển từ trạng thái con cấp 2 về trạng thái ông, trong đó phải chạy exit action của trạng thái cha. |
| 1706, 1707 | `TransitionGuard.cs:45,52`: `ToPackedGuards` cho trigger 2 và 3 tham số | real_gap | Các overload `PermitIf` nhiều guard với trigger 2 hoặc 3 tham số chưa có test nào gọi (NoCoverage). |
| 1581 | `StateRepresentation.cs:100`: `FirstOrDefault` thành `First` | equivalent | Khi đi tới dòng này, danh sách luôn có phần tử thỏa điều kiện. |
| 1633 | `StateRepresentation.cs:202`: đảo `IsIncludedIn` | equivalent | Ban đầu đánh giá là real_gap, **đã sửa lại sau lần chạy ứng viên**: `Exit()` của superstate tự kiểm tra lại đích đến, nên hành vi không đổi. |
| 1568 | `StateRepresentation.cs:80`: literal boolean | not_worth | NoCoverage ở một nhánh ít giá trị. |
| 1649, 1653 | Nội dung thông báo lỗi | not_worth | Chỉ đổi chữ trong thông báo. |
| 1652 | `StateRepresentation.cs:253`: `throw` phòng thủ | not_worth | Có vẻ không đi tới được qua API công khai. |
| 1715 | `TransitionGuard.cs:101`: `All` thành `Any` | not_worth | Hàm `GuardConditionsMet` bản sync không có chỗ gọi nào trong `src/`, chỉ test gọi tới. |

## Kết quả chạy chính thức (`after-tests`)

Commit ghim, phiên bản công cụ và phạm vi mutate giữ nguyên so với baseline. Sau khi mentor xác nhận, test trong `patches/`
được chạy chính thức với nhãn `after-tests` (trước đó là `candidate-tests`, cùng một bộ test, cùng kết quả — số liệu dưới
đây là từ lần chạy `after-tests`).

| Target | Mốc so sánh | Điểm trước | Điểm sau | Sống sót | NoCoverage | Thời gian |
| --- | --- | --- | --- | --- | --- | --- |
| Dinero.js | baseline lặp lại lần 1 | 347/359 = 96.7% | 354/359 = 98.6% | 11 → 5 | 1 → 0 | 114 s → 70.5 s |
| Stateless | baseline | 85/97 = 87.6% | 90/97 = 92.8% | 6 → 4 | 6 → 3 | 38 s → 43 s |

- **Dinero.js:** 9 test mới (4 file) bắt được cả 7 lỗ hổng thật. Mutant 297 và 298 bị bắt theo kiểu **Timeout**: khi bỏ nhánh chống treo,
  input `1e33` làm vòng lặp chạy mãi. Mutant 81 trước đây chỉ bị bắt nhờ may mắn, giờ bị bắt chắc chắn. 5 mutant còn lại
  đều là `equivalent` hoặc `not_worth`. Bảng chi tiết:
  [`dinero-repeat1-vs-after-tests.md`](comparisons/dinero-repeat1-vs-after-tests.md).
- **Stateless:** 4 test mới bắt được cả 5 lỗ hổng thật. 7 mutant còn lại (4 Survived, 3 NoCoverage) đều là `equivalent` hoặc
  `not_worth`. Bảng chi tiết: [`stateless-baseline-vs-after-tests.md`](comparisons/stateless-baseline-vs-after-tests.md).
- **Chỉ có một đề xuất bị sai** (mutant 1633): lần chạy có test ứng viên đã phát hiện ra, và verdict đã được sửa thành `equivalent`.

## Điều rút ra cho câu hỏi nghiên cứu

*"Test nào chạy qua code nhưng không bắt được thay đổi hành vi?"* Trong pilot này có 3 kiểu:

1. **Assertion chỉ kiểm tra kiểu exception** (Stateless 1579): hai lỗi khác nhau ném cùng một kiểu exception, nên test không phân biệt được.
2. **Ví dụ test bị điều kiện khác "che"** (Dinero 24/31/32): test tỉ lệ âm dùng input mà một điều kiện khác đã chặn từ trước,
   nên điều kiện cần kiểm tra chưa bao giờ quyết định kết quả.
3. **Test có tên đúng nhưng input không đi vào nhánh cần kiểm tra** (Dinero 297/298): tên test nói "không bị treo",
   nhưng input chia đều nên vòng lặp không chạy lần nào.

Thêm một hạn chế về độ tin cậy: **property test dùng seed ngẫu nhiên làm kết quả mutation testing không tất định**. Cùng commit,
cùng cấu hình mà mutant 81 lúc bị bắt, lúc không. Nên chạy lặp lại hoặc cố định seed của fast-check trước khi so sánh trước và sau.
