#Requires -Version 5.1
<#
  SessionStart hook — nhắc kỷ luật đầu phiên.

  In systemMessage ngắn nhắc: chủ đề đã CHỐT (QIGOA reality-check), và khi viết
  paper phải theo playbook chuẩn IEEE của thầy. Không bao giờ chặn phiên (exit 0).
#>

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$msg = 'Paper-3 (QIGOA reality-check) — chủ đề ĐÃ CHỐT (CLAUDE.md §1). Khi viết/sửa paper: theo docs/lam-va-viet-paper-chuan-IEEE.md (playbook thầy) + IRON RULES §2. Không bịa số/citation.'

$out = [ordered]@{ systemMessage = $msg }
$out | ConvertTo-Json -Depth 3 -Compress
exit 0
