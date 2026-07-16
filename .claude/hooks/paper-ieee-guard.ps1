#Requires -Version 5.1
<#
  UserPromptSubmit hook — Paper-writing compliance guard.

  Khi prompt của tác giả có ý định VIẾT / SỬA nội dung paper, hook này chèn
  additionalContext bắt buộc Claude đọc + tuân thủ playbook chuẩn IEEE của thầy
  (docs/lam-va-viet-paper-chuan-IEEE.md) và các IRON RULE trong CLAUDE.md §2/§4
  TRƯỚC khi viết một câu nào. Không trùng ý định viết paper => không chèn gì.

  Cơ chế: đọc JSON trên stdin (field "prompt"), so khớp keyword, in JSON có
  hookSpecificOutput.additionalContext. Luôn exit 0 (không bao giờ chặn prompt).
#>

$ErrorActionPreference = 'Stop'
try {
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch { }

# --- Đọc payload stdin an toàn ---------------------------------------------
$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

$prompt = ''
try {
    $data = $raw | ConvertFrom-Json
    if ($data.PSObject.Properties.Name -contains 'prompt') { $prompt = [string]$data.prompt }
} catch { }
# Fallback: nếu không lấy được field 'prompt' (tên field khác / JSON lạ), quét trên
# toàn chuỗi raw để hook không bao giờ im lặng nhầm. Text prompt luôn nằm trong raw.
if ([string]::IsNullOrWhiteSpace($prompt)) { $prompt = $raw }
if ([string]::IsNullOrWhiteSpace($prompt)) { exit 0 }

$p = $prompt.ToLowerInvariant()

# --- Keyword ý định viết / sửa paper (VI + EN) ------------------------------
# Giữ danh sách hẹp vào ĐỘNG TÁC viết + DANH TỪ section để tránh false-positive.
$patterns = @(
    'viết\s+(paper|bài|báo|section|phần|mục|abstract|introduction|related|method|kết\s*luận|thảo\s*luận|đóng\s*góp)',
    'viết\s+lại',
    'soạn\s+(paper|bài|section|phần)',
    'draft', 'bản\s*thảo', 'manuscript',
    'abstract', 'introduction', 'related\s+work', 'methodology', 'phương\s*pháp\s+đề\s*xuất',
    'formulation', 'hình\s*thức\s*hóa',
    'results?\s+section', 'discussion', 'kết\s*luận', 'conclusion',
    'rebuttal', 'phản\s*hồi\s+reviewer', 'response\s+to\s+reviewer',
    'chuẩn\s+ieee', 'ieee\s+transaction', 'theo\s+chuẩn\s+(tạp\s*chí|journal|ieee)',
    'chỉnh\s*sửa\s+(bài|paper|bản\s*thảo)', 'revise', 'revision',
    'academic-paper', 'academic-pipeline'
)

$hit = $false
foreach ($rx in $patterns) {
    if ($p -match $rx) { $hit = $true; break }
}
if (-not $hit) { exit 0 }

# --- additionalContext bắt buộc --------------------------------------------
$context = @'
[KỶ LUẬT VIẾT PAPER — BẮT BUỘC, tự động chèn bởi hook paper-ieee-guard]

Prompt này liên quan tới việc VIẾT hoặc SỬA nội dung paper. TRƯỚC KHI viết bất kỳ
câu nào, phải làm theo đúng thứ tự:

1. ĐỌC docs/lam-va-viet-paper-chuan-IEEE.md — playbook chuẩn IEEE Transactions do
   thầy Đỗ Phúc Hảo cung cấp. Đây là NGUỒN CHUẨN cho cách viết. Nếu cần bản gốc
   trực quan, xem 10 trang ảnh trong docs/lam-va-viet-paper-chuan-IEEE/. Viết ĐÚNG
   theo nó: formulation cứng (ký hiệu rõ, mục tiêu/ràng buộc/threat-model tường minh);
   evaluation là PHÉP THỬ BÁC BỎ (thiết kế để có thể làm sai claim của mình);
   related work là ĐỊNH VỊ + phân biệt near-rival, không liệt kê; đa-seed luôn luôn;
   anti-toy; reframe trung thực khi claim chính sụp.

2. TUÂN THỦ IRON RULES trong CLAUDE.md §2 & Definition of Done §8: KHÔNG bịa số,
   KHÔNG bịa citation, số chưa chạy ra từ script => [PLACEHOLDER]; không overclaim;
   caveat method + near-rival phải có mặt.

3. DÙNG skill `academic-paper` để viết/sửa section theo chuẩn journal (hoặc
   `academic-pipeline` cho trọn quy trình). KHÔNG viết tự do bỏ qua playbook.

Đây là quy tắc bắt buộc của dự án, KHÔNG phải gợi ý tùy chọn.
'@

$out = [ordered]@{
    hookSpecificOutput = [ordered]@{
        hookEventName    = 'UserPromptSubmit'
        additionalContext = $context
    }
}
$out | ConvertTo-Json -Depth 5 -Compress
exit 0
