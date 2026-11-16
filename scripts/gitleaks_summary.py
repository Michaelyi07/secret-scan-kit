#!/usr/bin/env python3
"""gitleaks_summary.py — build the CI Job Summary from a gitleaks JSON report.

Safety contract (ticket S2-INFRA-019 acceptance criterion #2):
the summary contains ONLY file path, line number, rule id and rule description.
The secret content is never read, never stored, never echoed — even if the
report was generated without --redact.
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def build_summary(report_path: str, out_path: str) -> int:
    with open(report_path, "r", encoding="utf-8") as f:
        findings = json.load(f)

    lines = ["# 🔐 Secret leak scan — FAILED", ""]
    lines.append(f"**Findings: {len(findings)}** (secret content is redacted and never displayed)")
    lines.append("")
    lines.append("| Rule | File | Line | Description |")
    lines.append("| --- | --- | --- | --- |")
    for f_ in findings:
        lines.append(
            f"| `{f_.get('RuleID', 'unknown')}` "
            f"| `{f_.get('File', '?')}` "
            f"| {f_.get('StartLine', '?')} "
            f"| {str(f_.get('Description', '')).replace('|', '\\|')} |"
        )
    lines.append("")
    lines.append("**What to do next:** follow `docs/secret-leak-runbook.md` "
                 "(rotate in KMS → revoke AccessKey → clean history → log & notify).")

    text = "\n".join(lines)
    # defense in depth: no raw secret material may ever appear in the summary
    import re
    if re.search(r'"?[Ss]ecret"?\s*[:=]', text) or re.search(
            r"LTAI[0-9A-Za-z]{10,28}\b", text):
        raise SystemExit("summary build aborted: raw secret material detected")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"summary written to {out_path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: gitleaks_summary.py <leaks.json> <output.md>")
        raise SystemExit(2)
    raise SystemExit(build_summary(sys.argv[1], sys.argv[2]))
