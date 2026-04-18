# Risk report (Sprint 3)

### Risks and GitLab work

| Risk ID | Related issues / MRs |
| ------- | -------------------- |
| R1      | #110    |
| R2      | #111    |
| R3      | -    |
| R4      | -    |
| R5      | -    |

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

### R3 — Poor Mobile Responsiveness

**Risk statement:** 
If mobile compatibility testing is skipped during development,
then the application UI may break or become unusable on smaller screens,
because the current Vue components are hardcoded primarily for desktop viewports.

**Likelihood (L):** High  
(Current stylesheets are missing flexible scaling or extensive `@media` queries.)

**Impact (I):** Medium  
(Backend logic remains intact, but degraded usability will negatively impact mobile users.)

**Owner:** Susie

**Mitigation or contingency:**
- **Mitigation:** Given the sprint deadlines, the team prioritized functional desktop delivery over mobile layouts. This limitation is formally acknowledged and documented.
- **Contingency:** A UI refactoring phase will be initiated in the next iteration to add CSS flexbox and media queries. Any critical layout breaks rendering the app unusable will be hotfixed.

**Evidence:**
- `frontend/src/style.css` (or global Vue styles) — absence of responsive `@media` utility coverage.
- `frontend/src/components/` — UI components utilizing fixed-width elements.

**Status:** accepted

**Last reviewed:** 2026-04-18

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

### R5 — API Gateway Timeout Under Load

**Risk statement:** 
If the application receives a sudden burst of high concurrent traffic,
then the server may temporarily block and drop user requests,
because the current architecture uses single-threaded synchronous WSGI workers.

**Likelihood (L):** Low  
(The application focuses on prototyping and currently experiences only minimal testing loads.)

**Impact (I):** High  
(Under production surges, this would cause HTTP 504 timeouts and unresponsiveness.)

**Owner:** Yulin Liu

**Mitigation or contingency:**
- **Mitigation:** Emphasizing MVP business logic correctly functioning was prioritized over extreme backend scalability. The default synchronous setup is completely sufficient for the current sprint scope.
- **Contingency:** If performance degrades during beta testing, we will tune worker scaling parameters in deployment. If long-term capacity maxes out, an ASGI evaluation will be triggered.

**Evidence:**
- `app.py` — standard synchronous APIFlask instantiation.
- `requirements.txt` / Deployment configurations — absence of asynchronous servers (like `uvicorn`) or non-blocking workers.

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
