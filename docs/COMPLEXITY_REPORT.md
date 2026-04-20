# COMP9820 Sprint 3: Complexity Report

**This file is wrote with help with generative ai tools.**

## 1. Essential vs. Accidental Complexity

In the TaskTracker project, our engineering decisions are evaluated continuously to differentiate between inherent problem complexity and complexity injected by our implementation details.

*   **Essential Complexity (Inherent):** The application *must* handle intricate user task states—including creation, scheduling (with and without due times), prioritization (task levels), and hierarchical categorization (pinned vs. unpinned). This complexity is mandatory to meet core user requirements and represent real-world task management systems faithfully.
*   **Accidental Complexity (Implementation-caused):** Initially, the logic for validating task properties (such as formatting due times, string length bounds, and casting booleans) was scattered monolithically within our route handlers or deeply embedded inline within our payload normalizers. This meant that whenever a task was processed (created or updated), the overlapping validation logic caused redundant loops and tangled try/catch blocks.

**Solution:** We extracted the complex `datetime.strptime()` logic and integer/string checks into pure helper functions (`_validate_task_title` and `_parse_due_time` within `modules/tasks/service.py`). This eliminated accidental duplication and localized the validation scope, allowing the system to scale its field validations cleanly. (See Commit `2a0afcf` / Issue `#58`).

---

## 2. Structural Improvements (Coupling & Cohesion)

As the backend scaled to handle both Task and User entity logic alongside JSON Web Token (JWT) tracking, the modules showed symptoms of tight coupling.

*   **Problem Identification:** The logic for deleting a task, verifying user ownership, and soft-deleting database entries in Sprint 2 was increasingly tightly coupled. A change in the database structure risked breaking the controller logic natively.
*   **Action Taken (Refactoring):** We formalized an aggressive **separation of concerns** by partitioning our backend strictly into a multi-tier architecture inside `modules/tasks/` and `modules/users/`. 
    *   **`routes.py` (Controllers):** Solely responsible for receiving HTTP requests, serializing inputs, and returning responses.
    *   **`service.py` (Business Logic):** Validates payloads, coordinates cross-system cleanup, and asserts user ownership.
    *   **`repo.py` (Data Access):** The strictly isolated ORM interacting layer.
*   **Why it Improved the System:** This structural improvement drastically enhanced **Maintainability and High Cohesion**. Changing how paths are routed does not break data interactions. A concrete example: when we added the scheduled soft-deletion feature, each layer was modified in isolation:
    *   [`bdf1bfd`](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/commit/bdf1bfd) added `cleanup_deleted_tasks` **only** to `repo.py` (pure ORM query, no business logic).
    *   [`0f461f9`](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/commit/0f461f9) wired the cleanup call into `routes.py` with **2 lines**, without touching any SQL model or business rule.
    *   [`3a7f691`](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/commit/3a7f691) consolidated all ownership verification (`task.user_id != user_id`) and payload validation **exclusively** into `service.py`, so neither `routes.py` nor `repo.py` needed to know about authorization rules.

    This demonstrates low coupling between layers: a database schema change only requires updating `repo.py`; a new business rule only touches `service.py`; neither change cascades to the other layers.

---

## 3. Cyclomatic Complexity (Case Study: Payload Normalization)

*   **Target Function:** The `_normalize(payload: dict) -> dict` function for task creation, located in `modules/tasks/service.py`.
*   **Why it was Complex:** This function is responsible for validating and normalising all task fields before persistence. It handles six fields (`task_title`, `task_due`, `task_description`, `task_level`, `is_finished`, `is_pinned`), and originally each field's validation logic was inlined directly inside the function body — `datetime.strptime()` format checking, string length guards, and integer casting all co-existed in one block. Each optional parameter added two to three independent execution paths, causing the function's cyclomatic complexity to reach **CC = 11 (Grade C)** as measured by radon on the state of `service.py` prior to commit [`2a0afcf`](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/commit/2a0afcf).

*   **Refactoring Applied:** We applied the **Extract Method** pattern, pulling the dense per-field validation out of `_normalize` and into two dedicated pure helper functions:
    *   `_validate_task_title(title: str)` — enforces non-empty and ≤ 100 character constraints
    *   `_parse_due_time(due: str)` — handles `datetime.strptime()` parsing and format validation

*   **Measured Outcome:** Running `radon cc modules/tasks/service.py -s` on the refactored codebase shows:

    ```
    _normalize          B (6)   ← was C (11) before extraction
    _parse_due_time     A (5)
    _validate_task_title A (4)
    ```

    `_normalize` dropped from **CC 11 → CC 6**, a reduction of 45%. Each extracted helper sits comfortably at CC ≤ 5 (Grade A), making them independently unit-testable. The function now acts purely as a field router — e.g. `due = _parse_due_time(payload.get("task_due"))` — with no nested branching inside the router body.

**Evidence Traceability:**
*   **Issue Refs:** [#55](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/issues/55) (Enhance title validation), [#58](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/issues/58) (Due date validation)
*   **Commit Refs:**
    *   [`2a0afcf`](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/commit/2a0afcf): *feat(tasks): add due time parsing and validation in task normalization (#58)*
    *   [`3845712`](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/commit/3845712): *fix(tasks): improve due date validation in task normalization (#58)*
    *   [`949559b`](https://gitlab.cse.unsw.edu.au/coursework/comp9820/26t1/groups/T09A-B/tasktracker/-/commit/949559b): *feat(tasks): enhance task title validation in normalization (#55)*
