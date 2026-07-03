# SessionStart hook for the QIGOA paper project.
# Injects a short research-integrity reminder + status into Claude's context each session.
# Safe: read-only, prints JSON to stdout, never blocks. See CLAUDE.md for the full rules.

$reminder = @'
[QIGOA project reminder - from .claude/hooks/session-reminder.ps1]
Research integrity is non-negotiable:
- Do NOT fabricate any experimental number, table value, p-value, or citation.
- The results in Huong-tiep-can-paper-Long.pdf are PLACEHOLDERS until reproduced on Kaggle.
- Every quantitative claim must trace to a re-runnable script output; every reference must be verifiable.
- Mark unverified content with [PLACEHOLDER] / [TODO] / [UNVERIFIED] — never silently promote it.
Skills available: deep-research, academic-paper, academic-paper-reviewer, academic-pipeline.
Full rules: CLAUDE.md. Communicate with the author in Vietnamese.
'@

$payload = @{
    hookSpecificOutput = @{
        hookEventName    = 'SessionStart'
        additionalContext = $reminder
    }
}

$payload | ConvertTo-Json -Compress -Depth 5 | Write-Output
