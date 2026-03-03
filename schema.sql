CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_title TEXT NOT NULL,
  task_due TEXT,                 -- store as ISO date string: 'YYYY-MM-DD'
  task_description TEXT,
  task_level INTEGER NOT NULL DEFAULT 0,
  is_finished INTEGER NOT NULL DEFAULT 0,  -- 0=false, 1=true
  is_deleted INTEGER NOT NULL DEFAULT 0,    -- 0=false, 1=true (soft delete)
);