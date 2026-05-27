# Security Policy

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, report vulnerabilities privately by emailing:

**pratikkaranje03@gmail.com**

Include as much detail as possible:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes

You will receive a response within 48 hours. We will work with you to
understand and resolve the issue before any public disclosure.

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x | ✅ Yes |

## Security Best Practices for Contributors

- Never commit `.env` files or API keys
- Never commit `data/chroma_db/` or model weights
- Use `uv add <package>` and pin versions in `pyproject.toml`
- Run `pip-audit` or `uv audit` before submitting a PR
