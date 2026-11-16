# tests/fixtures/dummy_keys.py
#
# ALL values in this file are fabricated dummies used ONLY by the
# leak-scanner unit tests. They are NOT real credentials.
#
# Exemption mechanism (two layers, per .gitleaks.toml):
#   1. inline `# gitleaks:allow` marker on each dummy line — reason stated inline;
#   2. exact-value regexes in the [allowlist] block of .gitleaks.toml — each entry
#      carries a reason comment there as well.
# Nothing outside tests/fixtures/ may ever use these markers.

# Fabricated Alibaba-Cloud-style AccessKey ID (starts with LTAI on purpose —
# used to prove the scanner catches LTAI-prefixed keys).
DUMMY_ACCESS_KEY_ID = "LTAI000000000000DEADDUCK"  # gitleaks:allow — fabricated AccessKey ID for scanner unit tests

# Fabricated paired AccessKey secret assignment.
access_key_secret = "DeAdDuCkSeCrEt00000000000000fake"  # gitleaks:allow — fabricated paired secret for scanner unit tests

# Fabricated JWT signing secret assignment.
jwt_signing_key = "jwt-signing-dummy-DO-NOT-USE-000000"  # gitleaks:allow — fabricated JWT signing secret for scanner unit tests

# Fabricated WeCom app secret assignment.
wecom_app_secret = "wecom-dummy-secret-DEADDUCK000000"  # gitleaks:allow — fabricated WeCom app secret for scanner unit tests

# Fabricated Feishu app secret assignment.
feishu_app_secret = "feishu-dummy-secret-DEADDUCK00000"  # gitleaks:allow — fabricated Feishu app secret for scanner unit tests

# Fabricated database DSN with a dummy password segment.
DUMMY_DSN = "postgresql://ci_user:dummy_pg_pw_deadduck@127.0.0.1:5432/ci_db"  # gitleaks:allow — fabricated DSN with dummy password for scanner unit tests
