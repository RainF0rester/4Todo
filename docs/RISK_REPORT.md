# Risk report (Sprint 3)

### Risks and GitLab work

| Risk ID | Related issues / MRs |
| ------- | -------------------- |
| R1      | #70 #88 !30     |
| R2      | #TODO_ISSUE_ID_2     |
| R3      | #TODO_ISSUE_ID_3     |
| R4      | #TODO_ISSUE_ID_4     |

---

## R1 — Inefficient Trigger for Scheduled Task Deletion

**Risk statement:** If the `clean_deleted_tasks` background cleanup function is only triggered passively through `get_task` and `list_tasks` API calls in `routes.py`, then tasks may not be deleted at their precise scheduled time, because the cleanup inherently relies on user traffic rather than a dedicated timer sequence. This also slightly increases API response latency.

**Likelihood (L):** High (guaranteed to delay cleanup if the system has no active users)

**Impact (I):** Low (leaves stale data temporarily in `SQLite` and causes minor API overhead, but does not block core functionalities given the current small user base)

**Owner:** Lucia Luo

**Mitigation or contingency:**
- **Mitigation:** We are intentionally adopting this "lazy execution" model as a simplified approach for Sprint 3. This risk is currently *accepted* due to our small scale.
- **Contingency:** In future iterations, we will decouple the cleanup logic from `routes.py` and replace it with a dedicated background task scheduler like `cron`, `APScheduler`, or `Celery`.

**Evidence link:** `modules/tasks/routes.py` (`clean_deleted_tasks` invoked inside `get_task` and `list_tasks`)

**Status:** accepted

**Last reviewed:** 2026-04-18

---

## Optional: monitoring (1–2 indicators per risk)

| Risk ID | How we know mitigation is working |
| ------- | --------------------------------- |
| R1      | Deleted tasks are successfully cleared from the DB as soon as someone triggers the API. |
