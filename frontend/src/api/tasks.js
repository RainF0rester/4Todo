// get task list

const TASKS_API = "/api/tasks";
const GUEST_KEY = "guest_tasks";
const GUEST_LIMIT = 8;

function isGuest() {
  return !!localStorage.getItem("authGuest");
}

function loadGuestTasks() {
  try {
    const raw = localStorage.getItem(GUEST_KEY);
    if (!raw) return [];
    return JSON.parse(raw);
  } catch (e) {
    return [];
  }
}

export function saveGuestTasks(tasks) {
  localStorage.setItem(GUEST_KEY, JSON.stringify(tasks));
}

function generateGuestId() {
  // negative timestamp id to avoid clashing with server ids
  return -Date.now();
}

function limitTaskLevel(v) {
  const n = Number(v);
  const result = n >= 1 && n <= 4 ? n : null;
  return result;
}

export function normalizeTask(t) {
  return {
    id: Number(t.id),
    title: t.task_title,
    dueDate: t.task_due ? t.task_due : "",
    done: t.is_finished ? true : false,
    task_level: limitTaskLevel(Number(t.task_level)),
  };
}

export async function getTaskList() {
  if (isGuest()) {
    const tasks = loadGuestTasks().filter((t) => Number(t.is_deleted) !== 1);
    return tasks.map(normalizeTask);
  }

  const res = await fetch(TASKS_API);
  if (!res.ok) throw new Error("Unable to get tasks list");
  const data = await res.json();
  return data.map(normalizeTask);
}

// add task
export async function addTask(task) {
  if (isGuest()) {
    const tasks = loadGuestTasks();
    if (tasks.length >= GUEST_LIMIT) {
      throw new Error(
        "Guest limit reached. Please login to create more tasks.",
      );
    }
    const now = new Date().toISOString();
    const newTask = {
      id: generateGuestId(),
      task_title: task.task_title,
      task_due: task.task_due || null,
      task_description: task.task_description || null,
      task_level: task.task_level || 0,
      is_finished: 0,
      created_at: now,
      updated_at: now,
      is_deleted: 0,
    };
    tasks.unshift(newTask);
    saveGuestTasks(tasks);
    return Promise.resolve(newTask);
  }

  const res = await fetch(TASKS_API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new Error(data?.message || "Unable to add task");
  }
  return res.json();
}

//edit task
export async function updateTask(id, task) {
  if (isGuest()) {
    const tasks = loadGuestTasks();
    const idx = tasks.findIndex((t) => Number(t.id) === Number(id));
    if (idx === -1) throw new Error("Unable to update task");
    const updated = {
      ...tasks[idx],
      ...task,
      updated_at: new Date().toISOString(),
    };
    tasks[idx] = updated;
    saveGuestTasks(tasks);
    return Promise.resolve(updated);
  }

  const res = await fetch(`${TASKS_API}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new Error(data?.message || "Unable to update task");
  }
  return res.json();
}

//delete task
export async function deleteTask(id) {
  if (isGuest()) {
    const tasks = loadGuestTasks();
    console.log("Deleting task with id", id, "from guest tasks", tasks);
    const idx = tasks.findIndex((t) => Number(t.id) === Number(id));
    if (idx === -1) throw new Error("Unable to delete task");
    // soft delete
    tasks[idx].is_deleted = 1;
    saveGuestTasks(tasks);
    return Promise.resolve({ status: "ok" });
  }

  const res = await fetch(`${TASKS_API}/${id}/delete`, {
    method: "PATCH",
  });
  if (!res.ok) throw new Error("Unable to delete task");
  return res.json();
}

export async function restoreTask(id) {
  if (isGuest()) {
    const tasks = loadGuestTasks();
    const idx = tasks.findIndex((t) => Number(t.id) === Number(id));
    if (idx === -1) throw new Error("Unable to restore task");
    tasks[idx].is_deleted = 0;
    saveGuestTasks(tasks);
    return Promise.resolve({ status: "ok" });
  }
  const res = await fetch(`${TASKS_API}/${id}/restore`, {
    method: "PATCH",
  });
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new Error(data?.message || "Unable to restore task");
  }
  return res.json();
}
