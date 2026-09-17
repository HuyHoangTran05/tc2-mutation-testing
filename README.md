# TC2 - Mutation Testing Pilot

Thí điểm **mutation testing** trên hai thư viện mã nguồn mở có quy tắc nghiệp vụ rõ ràng: một thư viện C# và một thư viện JavaScript.
Stryker cố ý sửa sai code theo từng chỗ nhỏ (mỗi bản sửa là một *mutant*), rồi chạy bộ test xem có test nào fail không.
Mutant **sống sót** (test vẫn pass) cho thấy test có chạy qua code nhưng không phát hiện được thay đổi hành vi.

**Câu hỏi nghiên cứu:** test nào chạy qua code nhưng không phát hiện được thay đổi hành vi?

## Mục tiêu

| Target | Ngôn ngữ | Quy tắc nghiệp vụ | Công cụ |
| --- | --- | --- | --- |
| [Dinero.js](https://github.com/dinerojs/dinero.js) | TypeScript | Phép tính, so sánh, đổi scale, làm tròn và chia tiền theo tỉ lệ (`core/api`, `core/utils`, `core/divide`) | StrykerJS + Vitest |
| [Stateless](https://github.com/dotnet-state-machine/stateless) | C# | Quy tắc chuyển trạng thái: guard, trigger bị bỏ qua, reentry | Stryker.NET + xUnit (net9.0) |

Commit của từng repo được ghim trong [`targets.toml`](targets.toml). Phạm vi mutate nằm trong [`config/`](config/).

## Cài đặt

Cần Python 3.11+, Git, Node.js 20+ (cho Dinero.js) và .NET SDK 10 kèm runtime 9 (cho Stateless).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q

# .NET SDK không cần quyền admin (cài vào %LOCALAPPDATA%\Microsoft\dotnet)
Invoke-WebRequest https://dot.net/v1/dotnet-install.ps1 -OutFile dotnet-install.ps1
.\dotnet-install.ps1 -Channel 10.0 -InstallDir "$env:LOCALAPPDATA\Microsoft\dotnet" -NoPath
.\dotnet-install.ps1 -Channel 9.0  -InstallDir "$env:LOCALAPPDATA\Microsoft\dotnet" -NoPath
```

## Sử dụng

```powershell
.\.venv\Scripts\python.exe -m tc2 setup dinero        # clone đúng commit, npm ci, cài StrykerJS
.\.venv\Scripts\python.exe -m tc2 setup stateless     # clone đúng commit, cài dotnet-stryker, restore
.\.venv\Scripts\python.exe -m tc2 run dinero --label baseline
.\.venv\Scripts\python.exe -m tc2 run stateless --label baseline
.\.venv\Scripts\python.exe -m tc2 summarize results\<thư mục> --reviewed data\reviewed\<target>.csv
```

Mỗi lần chạy tạo `results/<thời gian>-<target>-<nhãn>/` gồm:

| File | Nội dung |
| --- | --- |
| `run.json` | commit, thời gian chạy, exit code, phiên bản Node/npm/Stryker/Vitest hoặc .NET SDK/Stryker.NET/xUnit |
| `mutation.json` | báo cáo gốc của Stryker (đường dẫn đã chuyển về tương đối) |
| `summary.md` | điểm kèm mẫu số, số lượng theo trạng thái và theo file |
| `survivors.csv` | các mutant `Survived` / `NoCoverage` để review |
| `mutation.html`, `stryker.log` | chỉ có trên máy (không commit vì chứa đường dẫn máy) |

## Cách đọc kết quả

- **Killed:** có test bắt được thay đổi. **Survived:** test chạy qua nhưng không bắt được, đây là trọng tâm phân tích.
- **NoCoverage:** không test nào chạy qua. Đây là thiếu test, khác với test yếu, nên báo cáo tách riêng.
- **Timeout:** Stryker tính là bắt được, nhưng báo cáo liệt kê riêng.
- **CompileError / RuntimeError:** mutant không hợp lệ, bị loại khỏi mẫu số. Với Stryker.NET, số này có thể gồm cả file ngoài phạm vi mutate.
- **Equivalent:** mutant có hành vi giống hệt code gốc. Chỉ xác định được khi review tay (`verdict = equivalent`), và bị trừ khỏi mẫu số ở dòng điểm riêng.

## Review mutant sống sót

Copy `survivors.csv` của lần chạy baseline sang `data/reviewed/<target>.csv`, rồi điền:

| Cột | Giá trị |
| --- | --- |
| `verdict` | `real_gap` (lỗ hổng thật), `equivalent` (hành vi không đổi), `not_worth` (không đáng viết test, ví dụ nội dung thông báo lỗi) |
| `reason` | giải thích ngắn |
| `mentor_confirmed` | `yes` khi mentor đã xác nhận |

Test mới chỉ viết cho các `real_gap` mentor đã xác nhận. Sau đó chạy lại với `--label after-tests` để so trước và sau.

## Kết quả

### Baseline (17/09/2026)

| Target | Điểm (bắt được / hợp lệ) | Killed | Survived | NoCoverage | Timeout | Không hợp lệ | Thời gian |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dinero.js | 348/359 = 96.9% | 344 | 10 | 1 | 4 | 0 | 101 s |
| Stateless | 85/97 = 87.6% | 85 | 6 | 6 | 0 | 20 | 38 s |

Chi tiết: [`results/20260917-145130-dinero-baseline/`](results/20260917-145130-dinero-baseline/summary.md) và
[`results/20260917-145311-stateless-baseline/`](results/20260917-145311-stateless-baseline/summary.md).
Chưa review mutant nào, nên chưa có số equivalent.

- **Dinero.js:** 10 mutant sống sót, tập trung ở `allocate` (kiểm tra tỉ lệ âm), `trimScale`, `distribute`
  (vòng chia phần dư) và hai chỗ optional chaining.
- **Stateless:** 6 mutant sống sót và 6 NoCoverage, gần như toàn bộ ở `StateRepresentation.cs` và `TransitionGuard.cs`
  (ví dụ `All()` đổi thành `Any()` trong kiểm tra guard).

### Lần chạy thăm dò toàn thư viện Dinero.js

Không commit, cấu hình tạm. Lần chạy mất 28 phút, điểm 631/796 = 79.3%. Trong đó 152/164 mutant sống sót và 123 timeout
nằm ở bảng tiền tệ `bigint/currencies`, là dữ liệu chứ không phải quy tắc nghiệp vụ. Vì vậy phạm vi pilot bỏ phần này.
