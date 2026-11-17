# secret-scan-kit — Secret Leakage Protection (pre-commit + CI gate)

> **Delivery pin:** repo pinned at commit `76952af` (main, pushed 2026-11-17). All acceptance
> criteria are verified in **real GitHub Actions runs**: full-history scan on main PASSED
> ([run 43986619830](https://github.com/Michaelyi07/secret-scan-kit/actions/runs/43986619830));
> a demo PR with a fabricated, non-allowlisted LTAI key was rejected by CI, `leaks found: 1`
> ([run 43994209820](https://github.com/Michaelyi07/secret-scan-kit/actions/runs/43994209820),
> closed without merging). CI needs the checksum-verify fix included in `76952af` - do not
> revert to earlier commits.

Static configuration & workflow bundle for gitleaks-based secret-leak scanning
across the four top-level directories: `backend/`, `web/`, `miniprogram/`, `infra/`.
Static configuration & workflow bundle for gitleaks-based secret-leak scanning
across the four top-level directories: `backend/`, `web/`, `miniprogram/`, `infra/`.

## Deliverables

| File | Purpose |
| --- | --- |
| `.pre-commit-config.yaml` | pre-commit gate: gitleaks (custom rules), detect-private-key, check-added-large-files (2 MB limit) |
| `.gitleaks.toml` | Custom rule families: ① LTAI AccessKeys + paired secrets ② JWT signing key fields ③ WeCom/Feishu app secrets ④ PEM private keys ⑤ database DSN password segments. Allowlist covers only fabricated dummy values (the `tests/fixtures/` dummies and the demo key quoted by verification evidence), each with a reason comment |
| `.github/workflows/secret-scan.yml` | CI gate: gitleaks on every PR (all commits in the current PR) and every push to main; weekly scheduled full-history scan stored as an artifact; leak ⇒ job fails; Job Summary shows only file path, line number and rule name — never the secret |
| `scripts/gitleaks_summary.py` | Builds the redacted Job Summary from the gitleaks JSON report (field-limited output) |
| `docs/secret-leak-runbook.md` | Incident response: rotate in KMS → revoke cloud AccessKey → clean history with git filter-repo + force re-clone → log & notify |
| `tests/fixtures/dummy_keys.py` | Fabricated dummy values used by the exemption tests (each line carries an inline `# gitleaks:allow` reason marker) |
| `verification/VERIFICATION_LOG.md` | Real command outputs proving acceptance criteria #1–#4 |
| `verification/screenshots/` | Interception screenshots (pre-commit block, CI block, redacted Job Summary) |

## Integration

- Drop all files at the repository root (paths in the workflow/configs are root-relative and cover all four directories).
- No runtime dependencies; no third-party SDKs; all tooling runs in CI/pre-commit only.
- Integration points with other tickets: none (self-contained; uses GitHub Actions native features only).

## How to run

```bash
# 1. local pre-commit gate
pip install pre-commit
pre-commit install

# 2. CI gate — automatic on every PR / push to main (.github/workflows/secret-scan.yml)

# 3. manual full-history scan (same command CI uses for weekly scan)
gitleaks detect --source . --config .gitleaks.toml --redact \
  --report-format json --report-path leaks.json
```

## How to verify (acceptance criteria)

1. **Fake LTAI key caught by BOTH pre-commit and CI** — see `verification/VERIFICATION_LOG.md` §1/§2 and `verification/screenshots/screenshot_1_precommit_block.png`, `screenshot_2_ci_block.png`. A staged commit with a fake `LTAI…` key is blocked by the real pre-commit hook (exit 1); committing with the hook bypassed and scanning the PR commit range is blocked by the CI command (exit 1).
2. **Raw key never in the CI failure summary** — §3 and `screenshot_3_job_summary.png`: `--redact` + the field-limited summary script; grep of the raw key in the summary returns 0 hits.
3. **Dummy values under tests/fixtures with exemption comments do not fail** — §4: full-repo scan including `tests/fixtures/` returns exit 0 (inline `# gitleaks:allow` reason markers + exact-value allowlist entries with reason comments).
4. **Runbook has all four steps** — §5: rotation, revocation, history cleanup, notification all present in `docs/secret-leak-runbook.md`.

## Security notes

- All values in this bundle are fabricated; no real credentials anywhere.
- The allowlist may only ever contain fabricated dummy values (test fixtures
  and the demo key quoted by verification evidence); each entry must keep its reason comment.
- Scanning output is always generated with `--redact`; the summary script additionally never reads the secret field.
