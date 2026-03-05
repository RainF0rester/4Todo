// get task list
export async function getTaskList(){
    const res = await fetch('/api/tasks')
    if(!res.ok) 
        throw new Error('Unable to get tasks list')
    const data = await res.json()
    return data.map((t) => ({
      id: t.id,
      title: t.task_title,
      dueDate: t.task_due ? t.task_due : '',
      done: t.is_finished ? true : false,
      task_level: t.task_level != null ? t.task_level : 0
    }))
}

// add task
export async function addTask(task) {
    const res = await fetch('/api/tasks',{
        method: 'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(task),
    })
    if(!res.ok) 
        throw new Error('Unable to add task')
    return res.json()
}

