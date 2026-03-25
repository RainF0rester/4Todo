// get task list

const TASKS_API ='/api/tasks'

function limitTaskLevel(v) {
    const n = Number(v)
    const result = (n >= 1 && n <= 4) ? n : null
    return result
} 

export function normalizeTask(t){
    return{
        id: t.id,
        title: t.task_title,
        dueDate: t.task_due ? t.task_due : '',
        done: t.is_finished ? true : false,
        task_level: limitTaskLevel(t.task_level)}
}



export async function getTaskList(){
    const res = await fetch(TASKS_API)
    if(!res.ok) 
        throw new Error('Unable to get tasks list')
    const data = await res.json()
    return data.map(normalizeTask)
}

// add task
export async function addTask(task) {
    const res = await fetch(TASKS_API,{
        method: 'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(task),
    })
    if(!res.ok) {
        const data = await res.json().catch(() => null)
        throw new Error(data?.message || 'Unable to add task')}
    return res.json()
}

//edit task
export async function updateTask(id,task){
    const res = await fetch(`${TASKS_API}/${id}`,{
        method: 'PATCH',
        headers:{ 'Content-Type': 'application/json'},
        body: JSON.stringify(task)})
        if(!res.ok) {
            const data = await res.json().catch(() => null)
            throw new Error(data?.message || 'Unable to update task')}
            return res.json()
}
        
//delete task
export async function deleteTask(id) {
    const res = await fetch(`${TASKS_API}/${id}/delete`,{
        method: 'PATCH',
    })
    if(!res.ok) 
        throw new Error('Unable to delete task')
    return res.json()
}

export async function restoreTask(id){
   const res = await fetch(`${TASKS_API}/${id}/restore`, {
    method: 'PATCH',
  })
  if (!res.ok) {
    const data = await res.json().catch(() => null)
    throw new Error(data?.message || 'Unable to restore task')
  }
  return res.json()
}