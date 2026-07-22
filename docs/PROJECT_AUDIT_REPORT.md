# Project Audit Report — Apina — 2026-07-21

## Business Context

Apina is a lightweight API registry that exposes provider metadata and OpenAPI-derived endpoints through a REST API and an MCP server. Its core invariants are that provider definitions and schemas remain discoverable and that endpoint lookups should return consistent metadata without crashing the service. The system depends on local schema files plus a provider registry that loads metadata into memory for runtime use.

## Executive Summary

The repository is in a generally healthy state for a small service-oriented project, but it still has a few maintainability and resilience gaps. The most important issues are that provider discovery can fail hard when a schema is missing or malformed, and there is no automated test suite or coverage configuration for the Python service. The codebase is now better aligned with the repository’s documentation standards and linting rules after the documentation and typing updates.

---

## Findings

### P2 MEDIUM Provider discovery is fragile when a schema file is missing or invalid

| Field      | Value                                                         |
| ---------- | ------------------------------------------------------------- |
| Severity   | P2                                                            |
| Confidence | MEDIUM                                                        |
| Area       | Business Logic                                                |
| Location   | [service/api/v1/providers.py](../service/api/v1/providers.py) |

**What is wrong:**
The provider listing and endpoint discovery routes construct an OpenAPI parser for each provider without guarding against missing or invalid schema files. If a provider references an unreadable or malformed schema, the route can fail instead of degrading gracefully.

**Why it matters:**
This creates avoidable 500-style failures for one provider even when the rest of the registry is healthy, which weakens the reliability of the API for clients and agents.

**Evidence:**
The relevant code in [service/api/v1/providers.py](../service/api/v1/providers.py) creates a parser and immediately calls endpoint parsing without a surrounding recovery path.

**Recommendation:**
Wrap schema parsing in per-provider error handling, return an empty endpoint list or a clear provider-specific error payload, and log the failure so one bad schema does not break the overall response.

### P3 MEDIUM No automated tests or coverage config are present for the service

| Field      | Value             |
| ---------- | ----------------- |
| Severity   | P3                |
| Confidence | HIGH              |
| Area       | Test Coverage     |
| Location   | [tests](../tests) |

**What is wrong:**
The repository currently has no visible Python or JavaScript test suite files, and no pytest or Jest-style configuration was found in the workspace.

**Why it matters:**
This leaves core behaviors such as schema parsing, provider loading, and API routing unverified, increasing the risk of regressions during future changes.

**Evidence:**
The repository inspection returned no test files under [tests](../tests), and no test runner configuration files were present in the root.

**Recommendation:**
Add a small pytest suite for the parser and router modules, and add a basic coverage configuration so the service can be validated consistently.
