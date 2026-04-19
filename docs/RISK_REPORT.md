# Risk report (Sprint 3)

### Risks and GitLab work

| Risk ID | Related issues / MRs |
| ------- | -------------------- |
| R1      | #110    |
| R2      | #111    |
| R3      | MR !40    |
| R4      | MR !40    |
| R5      | #108   |

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
- Code changes in list_tasks / get_task (lazy deletion logic) MR !30 — Feat/sp3 lucia scheduled task deletion (#88)

Status:
accepted

Last reviewed:
2026-04-18

---

## R2 — Database Write-Contention and Transaction Bottleneck

**Risk statement:** If the application attempts to handle multiple concurrent `INSERT` or `UPDATE` transactions—such as a user rapidly clicking to delete 10 tasks simultaneously without frontend UI debouncing—then the system may encounter severe `OperationalError: db is locked` downtime, because the underlying single-file `SQLite` database fails to natively support concurrent writes.

**Likelihood (L):** Medium (Likelihood increases with lack of UI rate-limiting and normal traffic growth.)

**Impact (I):** High (Potential for unhandled HTTP 500s leading to data loss and severe SLA breaches.)

**Owner:** Yulin Liu

**Mitigation:**
The current design intentionally prioritizes simplicity and rapid development
to meet sprint goals. Potential scalability limitations (and missing frontend input debouncing) have been identified,
and future architectural improvements are planned.

**Contingency:**
If scalability issues arise, we will refactor the system incrementally
or plan a migration to a more robust architecture.

**Evidence:**
- Issue #111 — Evaluate migration to scalable architecture

**Status:** accepted

**Last reviewed:** 2026-04-18

---

## R3 — Poor Mobile Responsiveness

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
- MR !40 — Fix/Adjust feature details before sprint3 demo  
  (Includes fixes to mobile UI issues and highlights limitations in current responsive design)
- `frontend/src/style.css` — limited use of responsive layouts (`@media` queries)
- `frontend/src/components/` — components using fixed-width or desktop-oriented layouts

**Status:** accepted

**Last reviewed:** 2026-04-18

---

## R4 — Client–Server Time Inconsistency

**Risk statement:**
If task-related logic heavily depends on client-side device time, and the frontend validation logic lacks robustness against edge cases,
then task expiration and scheduling may be highly inconsistent or exploitable,
because client clocks may differ from server time, and insufficient validation allows malformed states to persist.

**Likelihood (L):** Medium  
(Client devices operate across diverse time zones, and legacy validation logic leaves gaps.)

**Impact (I):** Medium  
(Inconsistent task status or delayed/early expiration degrades system correctness and user trust.)

**Owner:** Susie

**Mitigation or contingency:**
- **Mitigation:** The backend is designated as the single source of truth for timestamps. Moving forward, robust frontend date validation will be re-implemented to act as a strict baseline before payload submission, while the backend recalculates and stores the authoritative time.
- **Contingency:** If rapid inconsistencies are observed (or bugs from weak previous validation arise), timestamps will be strictly validated against backend values, and legacy frontend display logic will be hotfixed.

**Evidence:**
- MR !40 — Fix/Adjust feature details before sprint3 demo  
  (Includes fixes to due date logic and frontend–backend consistency)

**Status:** open

**Last reviewed:** 2026-04-18

---

### R5 — Deployment and environment configuration risk

**Risk statement:**
If deployment and runtime configuration are inconsistent across local and deployed environments,
then the application may fail to build, run, or behave correctly in production,
because the project depends on multiple services and environment-specific settings.

**L / I:** Medium / High

**Owner:** Yulin Liu

**Mitigation or contingency:**
- Mitigation: The team introduced deployment-related files and environment setup changes to reduce configuration mismatch and improve deployment stability.
- Contingency: If deployment fails or behaves inconsistently, we will roll back to a known working configuration and apply targeted fixes to the deployment settings.

**Evidence:**
- Issue #108 — [US12-sp3] Deploy project
- MR !33 — add docker related files
- MR !34 — Feat/add cd files and fix some bugs
- MR !37 — deploy merge (#108)

**Status:** mitigated

**Last reviewed:** 2026-04-18

---

## Optional: Monitoring

### R1 — Delayed task cleanup
- Check whether expired tasks are removed during `get_task` and `list_tasks` operations.

### R2 — Lightweight design (future migration)
- Observe increasing complexity in service-layer logic or frequent refactoring needs.

### R3 — Mobile responsiveness
- Test UI layout on mobile viewport (e.g., browser dev tools) during demo or feature updates.

### R4 — Client–Server time inconsistency
- Compare client-displayed time and backend-stored timestamps when debugging inconsistencies.

### R5 — Deployment and environment configuration
- Verify application startup and API responses after deployment (e.g., via Docker or deployed environment).
