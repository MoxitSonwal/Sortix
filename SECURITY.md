# Security policy

Sortix handles sensitive filesystem paths. Please do not report vulnerabilities in public issues.

Email the maintainers privately with:

- a concise description of the issue
- reproducible steps using a temporary folder
- the affected version
- any suggested mitigation

Sortix's local API binds to `127.0.0.1` by default. Do not expose it to a network without adding authentication and a deliberate threat model.