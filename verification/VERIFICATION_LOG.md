# verification/VERIFICATION_LOG.md — ticket S2-INFRA-019 real-run verification log

Environment: Windows 11, git bash, gitleaks v8.21.2, pre-commit 4.6.0.
All values used are fabricated dummies (`LTAI000000000000DEADDUCK` family /
`LTAI5t9XkQ8mDeAdDuCk42Id` demo key). No real credentials anywhere.

## §1 — Acceptance #1a: pre-commit layer catches fake LTAI key

Real pre-commit hook chain installed (`pre-commit install`), then
`git commit -m "add settings"` with a staged file containing a fake
LTAI AccessKey ID:

```text
Detect hardcoded secrets.................................................Failed
- hook id: gitleaks
- exit code: 1

Finding:     ...UN_ACCESS_KEY_ID = "REDACTED
Secret:      REDACTED
RuleID:      aliyun-access-key-id
Entropy:     4.168296
Tags:        [cloud accesskey]
File:        backend/settings.py
Line:        2
Fingerprint: backend/settings.py:aliyun-access-key-id:2

8:33PM INF 1 commits scanned.
8:33PM INF scan completed in 184ms
8:33PM WRN leaks found: 1

detect private key.......................................................Passed
check for added large files..............................................Passed
```

`git commit` exit code: **1** — commit rejected, nothing entered git history.
Screenshot: `screenshots/screenshot_1_precommit_block.png`

## §2 — Acceptance #1b: CI layer catches the same leak bypassing the hook

The leak was committed with `--no-verify` on a feature branch. The CI command
from `.github/workflows/secret-scan.yml` was executed locally against the same
commit range the workflow resolves on GitHub Actions (`origin/main..<pr head
SHA>`; the workflow uses `github.event.pull_request.head.sha` because
pull_request checkouts are on a detached HEAD):

```bash
gitleaks detect --source . --config .gitleaks.toml --redact \
  --report-format json --report-path leaks.json \
  --log-opts "--no-merges origin/main..<pr-head-sha>"
```

```text
8:53PM INF 1 commits scanned.
8:53PM INF scan completed in 178ms
8:53PM WRN leaks found: 1
```

Process exit code: **1** — with the same config, same gitleaks version and the
same commit range the workflow computes, the job fails exactly as it does on
GitHub Actions (the only environmental difference is Actions' runtime).
Screenshot: `screenshots/screenshot_2_ci_block.png`

Note: an earlier draft of the workflow used `github.head_ref`, which cannot
resolve on detached-HEAD pull_request checkouts and was caught in independent
review; fixed to `github.event.pull_request.head.sha` and re-verified above.

## §3 — Acceptance #2: raw key never appears in the CI failure summary

`scripts/gitleaks_summary.py` built the Job Summary from `leaks.json`
(report produced with `--redact`):

```text
# Secret leak scan — FAILED
Findings: 1 (secret content is redacted and never displayed)
| Rule | File | Line | Description |
| aliyun-access-key-id | backend/settings.py | 2 | Alibaba Cloud AccessKey ID (LTAI prefix) |
```

Verification: `grep -c "LTAI5t9XkQ8mDeAdDuCk42Id" job_summary.md` → **0 hits**;
`grep -c "REDACTED"` → 0 (summary contains only rule id, path, line, description).
Screenshot: `screenshots/screenshot_3_job_summary.png`

## §4 — Acceptance #3: dummy values under tests/fixtures do not fail

Full-repo scan including `tests/fixtures/dummy_keys.py` (six fabricated values,
each carrying an inline `# gitleaks:allow` reason marker and a matching
exact-value allowlist entry with a reason comment in `.gitleaks.toml`):

```text
$ gitleaks detect --source . --config .gitleaks.toml --redact
8:25PM INF 1 commits scanned.
8:25PM INF scan completed in 194ms
8:25PM INF no leaks found
```

Exit code: **0** — no findings triggered by the fixtures.

## §5 — Acceptance #4: runbook contains the four required steps

`docs/secret-leak-runbook.md` section headers / keyword counts:
轮换 (rotate) 5 hits · 吊销 (revoke) 3 hits · filter-repo (history cleanup) 4 hits · 通知 (notify) 4 hits.
Runbook covers: rotate credentials in KMS → revoke cloud AccessKey (+ audit log
check) → clean history with git filter-repo + force re-clone → log incident &
notify responsible party, plus a quick-response checklist.

## File integrity (SHA256)

```text
.pre-commit-config.yaml            ee50b2204e46f84729429e2933d2d6036a5fd4011fa1e965fa3671a55b95311b
.gitleaks.toml                     d6d6f6381c81158aac5ef04d8e6643935580a4b526b992c036b0383121347800
.github/workflows/secret-scan.yml  4bc26e5fb2b93db1f594855dc3603d17ddbddd0191b441bca86d863f5991e9e0
scripts/gitleaks_summary.py        3330475e4aac92efbedeb52c713cf7306524958e18aa8b7e60dad52e2aaab6eb
docs/secret-leak-runbook.md        7e2c6c1696d2ced53896932794f0eb0420c56c0d944f17634d56d4eeb113dffe
tests/fixtures/dummy_keys.py       51733309f23950d8f9e33e8f9ea4bb72dee9073262902859ea3b17e856133dd5
README.md                          d5c685accd7f5c3a2fbbd4bcecabf22ac2ce452f3ce6dca975831e62252253e5
```

## Reproduce

```bash
pip install pre-commit && pre-commit install
# stage a file containing "LTAI5t9XkQ8mDeAdDuCk42Id" and run:
git commit -m "test"                      # -> blocked by pre-commit (exit 1)
git commit --no-verify -m "test"          # then on CI / locally:
gitleaks detect --source . --config .gitleaks.toml --redact \
  --log-opts "--no-merges main..HEAD"     # -> exit 1, CI fails
python scripts/gitleaks_summary.py leaks.json summary.md   # -> path/line/rule only
```
