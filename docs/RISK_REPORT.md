# Risk report (Sprint 3)

### Risks and GitLab work

| Risk ID | Related issues / MRs |
| ------- | -------------------- |
| R1      | #110    |
| R2      | #111    |
| R3      |    |
| R4      |    |
| R5      |    |

---

### R1 — Delayed task cleanup due to missing scheduler

**Risk statement:** 
If scheduled deletion is only triggered during task access (get/list),
then expired tasks may persist longer than expected,
because there is no background scheduler to enforce timely cleanup.

**Likelihood / Impact:**
Medium / Medium

**Owner:**
Lucia Luo

**Mitigation:**
Due to sprint time constraints and implementation complexity,
a full scheduler-based solution was not implemented.
Instead, a simplified lazy deletion mechanism was introduced
in get_task and list_tasks to partially reduce the impact.

**Contingency:**
If this issue affects system correctness, we will manually trigger cleanup
or deploy a hotfix to remove expired tasks.

**Evidence:**
- Issue #110 — Implement proper scheduled deletion mechanism
- Code changes in list_tasks / get_task (lazy deletion logic) !30

Status:
accepted

Last reviewed:
2026-04-18

---

## R2 — Database Write-Contention and Transaction Bottleneck

**Risk statement:** If the application scales to handle multiple concurrent `INSERT` or `UPDATE` transactions, then the system may encounter severe `OperationalError: db is locked` downtime, because the current persistence layer relies on a single-file `SQLite` database which uses coarse-grained file locks, natively failing to support concurrent writes.

**Likelihood (L):** Medium (Likelihood increases linearly with traffic growth.)

**Impact (I):** High (Potential for unhandled HTTP 500s leading to data loss and severe SLA breaches.)

**Owner:** Yulin Liu

**Mitigation:**
The current design intentionally prioritizes simplicity and rapid development
to meet sprint goals. Potential scalability limitations have been identified,
and future architectural improvements are planned.

**Contingency:**
If scalability issues arise, we will refactor the system incrementally
or plan a migration to a more robust architecture.

**Evidence:**
- Issue #111 — Evaluate migration to scalable architecture

**Status:** accepted

**Last reviewed:** 2026-04-18

---

### R3 — Poor mobile responsiveness and UI distortion

**Risk statement:** 
If mobile compatibility testing is skipped during development,
then the application UI may break or become unusable on smaller screens,
because the current Vue components are hardcoded primarily for desktop viewports.

**Likelihood / Impact:**
High / Medium

**Owner:**
Susie

**Mitigation:**
Given the tight sprint deadline, development focused primarily on core desktop functionality.
Mobile testing was deprioritized but has been flagged for subsequent sprints.

**Contingency:**
If critical mobile layout bugs block usage, we will deploy quick CSS hotfixes.
A dedicated UI CSS refactor is planned for the next iteration.

**Evidence:**
- Issue #112 — Implement responsive mobile UI
- Frontend CSS lacking `@media` queries

Status:
open

Last reviewed:
2026-04-18

---

### R4 — Client–Server Time Inconsistency

**Risk statement:**
If task-related logic depends on client-side device time,
then task expiration and scheduling may be inconsistent,
because client clocks may differ from server time.

**Likelihood (L):** Medium  
(Client devices may have incorrect system time or operate across time zones.)

**Impact (I):** Medium  
(Inconsistent task status or delayed/early expiration may affect user trust and system correctness.)

**Owner:** Susie

**Mitigation or contingency:**
- **Mitigation:** The backend is treated as the single source of truth for all task-related timestamps. Time values are stored and processed on the backend, while the frontend is responsible only for display.
- **Contingency:** If inconsistencies are observed, timestamps will be validated against backend values and frontend display logic will be adjusted accordingly.

**Evidence:**
- `schema.sql` — backend timestamp fields
- `modules/tasks/service.py` — timestamp processing logic
- frontend date handling (e.g., `utils/date.js`) — display formatting

**Status:** open

**Last reviewed:** 2026-04-18

---

### R5 — API Gateway timeout under load (Synchronous WSGI)

**Risk statement:** 
If the application receives a sudden burst of high-traffic or large file uploads,
then the server may completely block and drop user requests (504 errors),
because the current Flask architecture uses single-threaded synchronous WSGI workers.

**Likelihood / Impact:**
Low / High

**Owner:**
Yulin Liu

**Mitigation:**
In this sprint, the priority was proving business logic rather than extreme scalability. 
The current configuration is entirely sufficient for our small testing user base.

**Contingency:**
If server timeouts become frequent, we will immediately tune Gunicorn worker scaling,
or schedule a migration to an ASGI framework like FastAPI in a future sprint.

**Evidence:**
- Issue #114 — Evaluate asynchronous server framework (ASGI)
- `app.py` standard synchronous setup

Status:
accepted

Last reviewed:
2026-04-18

---

## Optional: monitoring (1–2 indicators per risk)

| Risk ID | Triggers & SLI Monitoring (How we know mitigation is working) |
| ------- | ----------------------------------------------------------- |
| R1      | P99 API Latency on `get_task` remains stable. No CPU spiking observed during standard traffic loads. |
| R2      | Alert triggered if `OperationalError: db is locked` error rate exceeds 1% of total transactions over a 1-hour window in Sentry/Log. |
| R3      | Automated CI viewport tests pass targeting `375px` and `768px` breakpoints successfully. |
| R4      | Backend test coverage confirms 100% of serialized timestamp outputs rely on UTC contexts, with 0 client-time dependencies. |
| R5      | Monitoring API Gateway/Nginx metrics to ensure 0 HTTP 504 Gateway Timeout or Dropped Connection events. |
