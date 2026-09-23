# Commit & Branch Naming Convention

## Commit Messages

Format: `<type>: <description>`

### Types

| Type       | When to use                        | Example                                           |
| ---------- | ---------------------------------- | ------------------------------------------------- |
| `feat`     | New feature                        | `feat: add redis temporary memory`                |
| `fix`      | Bug fix                            | `fix: fix token not refreshed bug`                |
| `refactor` | Code change with no behaviour change | `refactor: move backend source into backend/`     |
| `test`     | Adding or updating tests           | `test: add pomodoro related tests`                |
| `doc`     | Documentation only                 | `doc: update risk report`                        |
| `chore`    | Build, CI, dependencies            | `chore: update CI pipeline`                       |

### Rules

- All lowercase; one space after the colon
- Description in English, imperative tense, no trailing period
- Keep it short and clear — 72 characters max
- No scope needed (avoid `feat(auth): ...` style)

---

## Branch Names

Format: `<type>/<description>`

### Branch Types

| Type      | When to use           | Example                          |
| --------- | --------------------- | -------------------------------- |
| `feature` | Feature development   | `feature/ai-assistant`           |
| `fix`     | Bug fix               | `fix/api-cors`                   |
| `test`    | Test-only branches    | `test/backend-login`             |
| `docs`    | Documentation updates | `docs/update-readme`             |
| `chore`   | CI / tooling changes  | `chore/ci-pipeline`              |

### Branch Rules

- Use `-` to separate words, no underscores or spaces
- Delete branches after merging

---

## Examples

```text
# Commits
feat: add chat bot
fix: fix frontend request wrong api bug
refactor: move backend source into backend/ directory
test: add pomodoro related tests
docs: update README

# Branches
feature/ai-assistant
feat/frontend-task-filtering
fix/api-cors
test/backend-login
```
