# COMP9820 Sprint 3: Complexity Report

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
*   **Why it Improved the System:** This structural improvement drastically enhanced **Maintainability and High Cohesion**. Changing how paths are routed does not break data interactions. For example, when adding soft deletion (`cleanup_deleted_tasks`), it was safely wired up to the `service.py` layer without touching SQL models. 
*   **Evidence:** See Commit `0f461f9` (integrating cleanup of deleted tasks into the list API) and Commit `3a7f691` (enhancing task validations isolated in `service.py`).

---

## 3. Cyclomatic Complexity (Case Study: Payload Normalization)

*   **Target Function:** The `_normalize_update(payload: dict) -> dict` function (and the overlapping `_normalize()` function for task creation) located in `modules/tasks/service.py`.
*   **Why it was Complex:** This master function is responsible for determining which fields of a task require an update. It iterates over a highly variable parameter subset (`task_title`, `task_due`, `task_description`, `task_level`, `is_finished`, `is_pinned`). Originally, the inner loop of every single dictionary key featured dense, multi-branch conditional checks. For example, processing `"task_due"` meant catching bad string formats and tracking negative offsets, raising validation errors synchronously. The cyclomatic complexity was excessive since every optional parameter added two to three unique execution paths (branches).
*   **Refactoring Applied:** We actively refactored the function using the **Extract Method** pattern. We stripped the inner conditional complexity out of the generic handler and delegated it. We created:
    *   `_validate_task_title(title: str)`
    *   `_parse_due_time(due: str)`
*   **How Complexity was Reduced:** The `_normalize_update` function now simply acts as a deterministic dictionary router. Instead of deep conditionals checking data validity, it simply maps `data["task_due"] = _parse_due_time(payload.get("task_due"))`. The cyclomatic complexity per function dropped dramatically, resulting in code that is easier to unit test, read, and maintain. 

**Evidence Traceability:** 
*   **Issue Ref:** `#55` (Enhance title validation), `#58` (Due date validation)
*   **Merge/Commit Refs:** 
    *   `3845712`: *fix(tasks): improve due date validation in task normalization (#58)* 
    *   `2a0afcf`: *feat(tasks): add due time parsing and validation in task normalization (#58)*
    *   `949559b`: *feat(tasks): enhance task title validation in normalization (#55)*
