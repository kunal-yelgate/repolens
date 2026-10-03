"""Security patterns for secret scanning and vulnerability checks."""

import re
from typing import Any, Dict, Pattern

SECRET_PATTERNS: Dict[str, Pattern] = {
    "AWS Access Key": re.compile(r'(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'),
    "AWS Secret Key": re.compile(r'(?i)aws_secret_access_key\s*=\s*[\'"][A-Za-z0-9/+=]{40}[\'"]'),
    "GitHub Personal Access Token": re.compile(r'gh[pousr]_[A-Za-z0-9_]{36,255}'),
    "Generic Private Key": re.compile(r'-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PRIVATE)\s+KEY-----'),
    "Stripe API Key": re.compile(r'(?:sk|pk)_(?:test|live)_[0-9a-zA-Z]{24,}'),
    "Slack Webhook / Token": re.compile(r'xox[baprs]-[0-9a-zA-Z]{10,48}'),
    "SendGrid API Key": re.compile(r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}'),
    "OpenAI / Anthropic API Key": re.compile(r'sk-(?:proj-)?[a-zA-Z0-9]{20,80}'),
    "Hardcoded Password Assignment": re.compile(r'(?i)(?:password|passwd|secret_key|api_secret)\s*=\s*[\'"][^\'"]{6,}[\'"]'),
}

VULNERABILITY_PATTERNS: Dict[str, Dict[str, Any]] = {
    "dangerous_eval": {
        "pattern": re.compile(r'\beval\s*\('),
        "title": "Use of dangerous eval() function",
        "severity": "HIGH",
        "recommendation": "Avoid using eval() on untrusted inputs as it can lead to arbitrary code execution.",
    },
    "unsafe_subprocess": {
        "pattern": re.compile(r'subprocess\.(?:Popen|call|run|check_output)\s*\([^)]*shell\s*=\s*True'),
        "title": "Subprocess executed with shell=True",
        "severity": "MEDIUM",
        "recommendation": "Pass command arguments as a list without shell=True to prevent command injection.",
    },
    "insecure_cors": {
        "pattern": re.compile(r'allow_origins\s*=\s*\[\s*[\'"]\*[\'"]\s*\]'),
        "title": "Permissive CORS wildcard (*)",
        "severity": "MEDIUM",
        "recommendation": "Restrict allowed CORS origins to specific trusted domains in production.",
    },
    "debug_mode_enabled": {
        "pattern": re.compile(r'(?:debug\s*=\s*True|DEBUG\s*=\s*True)'),
        "title": "Debug mode enabled in code",
        "severity": "LOW",
        "recommendation": "Ensure debug mode is disabled or configured exclusively via environment variables in production.",
    },
    "sql_injection_concat": {
        "pattern": re.compile(r'execute\s*\(\s*f[\'"]SELECT|execute\s*\(\s*f[\'"]INSERT|execute\s*\(\s*f[\'"]UPDATE', re.IGNORECASE),
        "title": "Potential SQL injection via f-string formatted query",
        "severity": "HIGH",
        "recommendation": "Use parameterized queries or ORM query builders rather than string formatting.",
    },
}
