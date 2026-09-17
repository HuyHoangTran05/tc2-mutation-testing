# CLAUDE.md

Hướng dẫn cho Claude Code (và người mới) khi làm việc trong repo này.

**Bắt đầu phiên mới:** đọc `README.md` (kết quả hiện tại), `targets.toml`, và `summary.md` của lần chạy mới nhất trong `results/`.

## Dự án

TC2 - mutation testing pilot (intern project VSF, mentor: xem `../ASSIGNMENT.md`). Chạy Stryker trên một module có quy tắc
nghiệp vụ, review các mutant sống sót, viết test cho vài lỗ hổng mentor xác nhận, rồi so sánh trước và sau.

- **Câu hỏi nghiên cứu:** test nào chạy qua code nhưng không phát hiện được thay đổi hành vi?
- **Đánh giá:** mutant bị bắt trước/sau, thời gian chạy, số mutant sống sót đáng xử lý. Equivalent, invalid
  (CompileError/RuntimeError) và timeout **luôn báo cáo riêng**.
- **Stack do mentor chỉ định:** Stryker.NET (C#) và StrykerJS (JS), dùng báo cáo JSON/HTML và một CSV survivor đã review.

Chỉ dùng repo **mã nguồn mở** (Dinero.js, Stateless). Không đưa code hay dữ liệu nội bộ DMS vào repo này.

## Môi trường

- Windows, PowerShell. Python trong `.venv`: gọi `.\.venv\Scripts\python.exe -m ...` (không cần activate).
- Node.js 22 trên PATH. .NET SDK 10.0 + 9.0 cài theo user ở `%LOCALAPPDATA%\Microsoft\dotnet`, **không có trên PATH**;
  `tc2/common.py` (`dotnet_exe`, `dotnet_env`) tự tìm và đặt `DOTNET_ROOT`. Tự gọi dotnet trong PowerShell thì đặt
  `$env:DOTNET_ROOT` và thêm vào `$env:PATH` trước. Trong Git Bash, đường dẫn Windows không dùng được trong PATH.
- `targets/` là các repo clone về (gitignore). Tạo lại bằng `python -m tc2 setup <target>`.

## Lệnh thường dùng

```powershell
.\.venv\Scripts\python.exe -m pytest -q                        # phải xanh trước khi commit
.\.venv\Scripts\python.exe -m tc2 setup <dinero|stateless>     # clone đúng commit + cài Stryker
.\.venv\Scripts\python.exe -m tc2 run <target> --label <nhãn>  # chạy Stryker -> results/<thời gian>-<target>-<nhãn>/
.\.venv\Scripts\python.exe -m tc2 summarize <results-dir> --reviewed data\reviewed\<target>.csv
```

Thời gian tham khảo: Dinero.js phạm vi pilot khoảng 30 giây, Stateless khoảng 50 giây. Mở rộng `mutate` ra toàn thư viện
có thể mất hàng chục phút; chạy thử phạm vi rộng thì dùng file cấu hình tạm ngoài repo, không sửa config đang dùng cho baseline.

## Cấu trúc

| Đường dẫn | Vai trò |
| --- | --- |
| `targets.toml` | repo, commit ghim, thư mục làm việc, file cấu hình Stryker, phiên bản Stryker của từng target |
| `config/dinero.stryker.config.json` | StrykerJS: runner vitest, `mutate` = `core/divide`, `distribute`, `allocate` |
| `config/stateless.stryker-config.json` | Stryker.NET: chạy trong `src/Stateless`, test project ở `test/Stateless.Tests`, net9.0 |
| `tc2/__main__.py` | CLI; lệnh mới phải thêm vào `COMMANDS` |
| `tc2/common.py` | load target, tìm `dotnet`/`npx`, chạy subprocess |
| `tc2/setup.py` | clone theo SHA (`git fetch --depth 1 origin <sha>`), `npm ci --ignore-scripts`, `dotnet tool install` |
| `tc2/run.py` | chạy Stryker, ghi `run.json` (phiên bản công cụ), chuyển đường dẫn báo cáo về tương đối, gọi summarize |
| `tc2/summarize.py` | đọc báo cáo mutation-testing-elements (chung cho cả hai Stryker), viết `summary.md`, `survivors.csv` |
| `data/reviewed/<target>.csv` | survivor đã review tay (`verdict`, `reason`, `mentor_confirmed`) |
| `results/` | kết quả từng lần chạy; `mutation.html` và `stryker.log` không commit |
| `tests/` | pytest, không gọi mạng và không chạy Stryker thật |

## Quy ước kết quả (quan trọng)

- **Không sửa code của target** (`targets/`), trừ khi thêm test mới cho lỗ hổng đã được mentor xác nhận. Test mới cần được
  lưu lại trong repo này (ví dụ `patches/<target>/`), vì `targets/` không được commit.
- **Không đổi commit ghim, phiên bản Stryker hay phạm vi `mutate`** giữa lần chạy baseline và `after-tests`; nếu buộc phải
  đổi thì chạy lại baseline và ghi rõ lý do.
- `results/<run>/` là **bằng chứng, không sửa tay**. Muốn tính lại thì dùng `tc2 summarize`.
- Điểm luôn ghi kèm mẫu số (`85/97 = 87.6%`). Không gộp NoCoverage với Survived khi kết luận về chất lượng test.
- `verdict` chỉ nhận `real_gap`, `equivalent`, `not_worth` hoặc để trống. Claude có thể đề xuất verdict nhưng phải ghi rõ
  trong `reason`; chỉ người dùng hoặc mentor điền `mentor_confirmed`.
- Test mới phải có giá trị kỳ vọng độc lập, không chép lại chính công thức của code đang được test.
- Báo cáo JSON của Stryker.NET chứa cả file ngoài phạm vi (trạng thái `Ignored`), và số CompileError có thể gồm cả các file đó.

## Code

- Code, comment, docstring, thông điệp CLI: tiếng Anh. README, docs, báo cáo cho người đọc: tiếng Việt.
- Chỉ dùng thư viện chuẩn Python (pytest cho test). Hàm nhỏ, `from __future__ import annotations`, mỗi lệnh có `main(argv)`.
- Tính năng mới cần có test trong `tests/`.

## Git

- **Mỗi commit chỉ làm một việc** (một tính năng, một bản sửa, một lần chạy kết quả, một cập nhật docs) để dễ debug và
  `git revert`. Không gộp code, cấu hình và kết quả vào cùng một commit. Push sau mỗi commit.
- Nội dung commit tiếng Anh, dòng đầu ngắn gọn ở thể mệnh lệnh, kết thúc bằng dòng `Co-Authored-By`.
- PowerShell 5.1 làm vỡ dấu nháy kép trong `git commit -m`: ghi message ra file UTF-8 (không BOM) rồi `git commit -F <file>`.
- Repo là **private** trên GitHub (`HuyHoangTran05/tc2-mutation-testing`).
