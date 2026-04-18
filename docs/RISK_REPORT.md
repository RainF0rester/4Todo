# Risk report (Sprint 3)

### Risks and GitLab work

| Risk ID | Related issues / MRs |
| ------- | -------------------- |
| R1      | #70 #88 !30     |
| R2      | !2     |
| R3      | #TODO_ISSUE_ID_3     |
| R4      | #TODO_ISSUE_ID_4     |
| R5      | #TODO_ISSUE_ID_5     |

---

## R1 — Synchronous Background Task Coupling (Architectural Scalability Risk)

**Risk statement:** If automated background processes (such as `clean_deleted_tasks`) are tightly coupled to synchronous user-facing API requests, then the system may experience unpredicted tail latency degradation (P99 spikes) and violate the Single Responsibility Principle (SRP). 

**Likelihood (L):** High (This bottleneck occurs predictably during concurrent request surges.)

**Impact (I):** Medium (While currently stable under small user bases, this architectural flaw will block horizontal scaling in production.)

**Owner:** Lucia Luo

**Mitigation or contingency:**
- **Mitigation:** Document this as an accepted technical debt for Sprint 3. We intentionally adopt this "lazy execution" model as a simplified MVP approach.
- **Contingency:** For the next architectural iteration, decouple the cleanup logic from `routes.py` and replace it with a dedicated asynchronous background task scheduler (e.g., `Celery`, `Redis Queues`, or `cron`).

**Evidence link:** `modules/tasks/routes.py` (`clean_deleted_tasks` invoked inside `get_task` and `list_tasks`)  - issues: #70 #88 | merge requests: !30

**Status:** accepted

**Last reviewed:** 2026-04-18

---

## R2 — Database Write-Contention and Transaction Bottleneck

**Risk statement:** If the application scales to handle multiple concurrent `INSERT` or `UPDATE` transactions, then the system may encounter severe `OperationalError: db is locked` downtime, because the current persistence layer relies on a single-file `SQLite` database which uses coarse-grained file locks, natively failing to support concurrent writes.

**Likelihood (L):** Medium (Likelihood increases linearly with traffic growth.)

**Impact (I):** High (Potential for unhandled HTTP 500s leading to data loss and severe SLA breaches.)

**Owner:** Yulin Liu

**Mitigation or contingency:** 
- **Mitigation:** We have proactively abstracted our data access layer via `repo.py` to decouple business logic from the ORM.
- **Contingency:** If the concurrency error rate surpasses our predefined SLI threshold, we will execute our database migration plan, hot-swapping the `SQLALCHEMY_DATABASE_URL` in `config.py` from SQLite to a robust RDBMS (e.g., `PostgreSQL`), requiring zero changes to the core service layer.

**Evidence link:** `config.py` (Line 4: `SQLALCHEMY_DATABASE_URL = "sqlite:///taskmaster.db"`) | merge requests: !2

**Status:** open

**Last reviewed:** 2026-04-18

---

## R3 — Inadequate Viewport Adaptability Leading to UX Degradation

**Risk statement:** If our Definition of Done (DoD) lacks mandatory viewport testing and mobile-first CSS (`@media` breakpoints), then the frontend DOM elements risk severe layout distortion on smaller screens post-deployment, severely limiting our market reach for mobile-centric end-users.

**Likelihood (L):** High (Current production audits have already confirmed fragmented UX on mobile viewports.)

**Impact (I):** Medium (While backend logic remains intact, this critically degrades product usability and user retention.)

**Owner:** Susie

**Mitigation or contingency:** 
- **Mitigation:** Augment our agile DoD to mandate viewport adaptability validation for all future frontend tickets prior to merging.
- **Contingency:** Create and prioritize a "fast-follow" UI refactor Epic in GitLab. Implement headless browser viewport testing (e.g., Cypress/Playwright) in our CI pipeline to catch CSS regressions systematically.

**Evidence link:** Frontend CSS stylesheets / Vue Components (Lack of responsive `@media` utility classes)

**Status:** open

**Last reviewed:** 2026-04-18

---

## R4 — Distributed State Synchronization Risk (Client-Trust Vulnerability)

**Risk statement:** If the backend explicitly relies on or mirrors the client's localized device clock for task logic, then the UI might misrepresent task expiration metrics due to a temporal state inconsistency, fundamentally violating the "Never trust the client" (Zero Trust) security principle.

**Likelihood (L):** Medium (Highly probable for users operating across multiple time zones or misconfigured local clocks.)

**Impact (I):** High (Can trigger premature data purging, rendering critical user schedules unreliable.)

**Owner:** Susie

**Mitigation or contingency:** 
- **Mitigation:** Designate the backend SQLite/Database as the "Single Source of Truth". Standardize all API payloads to transmit purely in ISO-8601 UTC formats, delegating local timestamp transformation entirely to the Vue presentation layer.
- **Contingency:** Expose a resilient `/sys/time` fallback endpoint to proactively audit and synchronize the temporal delta between the server and the local device upon application bootstrap.

**Evidence link:** `schema.sql` (Timestamps handled dynamically without strict UTC isolation constraints) & Frontend Date modules.

**Status:** open

**Last reviewed:** 2026-04-18

---

## R5 — WSGI Synchronous Blocking Architecture Under High Concurrency

**Risk statement:** If the application encounters traffic surges or I/O-intensive operations (e.g., handling bulky uploads or waiting on external APIs), then the server may begin blocking entirely and dropping requests with HTTP Gateway Timeouts (504s), because the underlying Flask (APIFlask) implementation relies on single-threaded synchronous WSGI workers which cannot non-blockingly multiplex connections.

**Likelihood (L):** Low (Unlikely to manifest in the current prototyping phase with minimal active load.)

**Impact (I):** Critical (Complete service unavailability and severe drop in throughput under production load phenomena like a "thundering herd".)

**Owner:** [Your Architecture Lead]

**Mitigation or contingency:** 
- **Mitigation:** Document this framework constraint. For Sprint 3, ensure we properly configure our production Gunicorn cluster (e.g., in `supervisord.conf` or `docker-compose.yml`) to scale up multiple worker processes (`--workers=4` or `--threads=2`) to partially absorb the load.
- **Contingency:** For future phases that necessitate hundred-thousand tier connection loads, migrate Python middleware logic to an asynchronous `ASGI` gateway framework (e.g., FastAPI, Quart) leveraging native `async/await` non-blocking I/O alongside `Uvicorn`.

**Evidence link:** `app.py` & standard WSGI Flask architecture without explicit async abstractions.

**Status:** accepted

**Last reviewed:** 2026-04-18

---

## Optional: monitoring (1–2 indicators per risk)

| Risk ID | Triggers & SLI Monitoring (How we know mitigation is working) |
| ------- | ----------------------------------------------------------- |
| R1      | P99 API Latency on `get_task` remains stable. No CPU spiking observed during standard traffic loads. |
| R2      | Alert triggered if `OperationalError: db is locked` error rate exceeds 1% of total transactions over a 1-hour window in Sentry/Log. |
| R3      | Automated CI viewport tests pass targeting `375px` and `768px` breakpoints successfully. |
| R4      | Backend test coverage confirms 100% of serialized timestamp outputs rely on UTC contexts, with 0 client-time dependencies. |
| R5      | Monitoring API Gateway/Nginx metrics to ensure 0 HTTP 504 Gateway Timeout or Dropped Connection events. |
