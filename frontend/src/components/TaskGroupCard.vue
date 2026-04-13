<template>
  <a-card class="cards-group" :style="cardStyle" :bodyStyle="{ padding: 0 }">
    <!-- header -->
    <div class="header" :style="headerStyle">
      <div class="title">{{ title }}</div>
      <a-button size="small" class="add-btn" @click="showAddDialog">+</a-button>
    </div>

    <!-- list -->
    <!-- <div class="card-body"> -->
    <div class="card-body" :style="{ backgroundColor: palette[color]?.body }">
      <a-list :data-source="task_info" class="task-list" :pagination="{ pageSize: 3 }">
        <template #renderItem="{ item }">
          <a-list-item class="row" :class="{
            'pending-delete-row': item.pendingDelete,
            'deleting-row': item.deleting
          }">
            <div class="left">
              <a-checkbox :class="{ invisible: item.pendingDelete }" :disabled="!canComplete(item.dueDate)"
                :checked="item.done" @change="(e) => toggleDone(item, e.target.checked)" />
              <div class="text" @click="showEditDialog(item)">
                <a-tooltip :title="item.title.length > 15 ? item.title : null">
                  <div class="name" :class="{ done: item.done }" @click="!item.pendingDelete && showEditDialog(item)">
                    {{ item.title }}
                  </div>
                </a-tooltip>
                <div v-if="item.dueDate" class="meta">{{ dueText(item.dueDate) }}</div>
              </div>
            </div>
            <div class="right">
              <a-tooltip v-if="!item.done && getDueStatus(item.dueDate) === 'overdue'" :title="dueTooltip(item.dueDate)"
                placement="top">
                <a-button type="text" class="overdue-btn" :class="{ invisible: item.pendingDelete }">
                  <ExclamationCircleOutlined />
                </a-button>
              </a-tooltip>

              <a-tooltip v-else-if="getDueStatus(item.dueDate) === 'warning'" :title="dueTooltip(item.dueDate)"
                placement="top">
                <a-button type="text" class="warning-btn" :class="{ invisible: item.pendingDelete }">
                  <WarningOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip :title="item.pinned ? 'Unpin task' : 'Pin task'">
                <a-button type="text" class="pin-btn" danger :class="{ pinned: item.pinned }" @click="togglePin(item)">
                   <PushpinOutlined />
                </a-button>
              </a-tooltip>

              <a-button v-if="!item.pendingDelete" type="text" danger @click="remove(item.id)">

                <DeleteOutlined />
              </a-button>
              <a-button v-else type="text" class="undo-btn countdown" @click="undoRemove(item.id)">
                <RedoOutlined />
              </a-button>
            </div>
          </a-list-item>
        </template>
      </a-list>
    </div>
  </a-card>
  <TaskModal v-model:open="open" :mode="modalMode" :task="editingTask" :people="peopleOptions" @submit="handleSubmit" />
</template>

<script setup>
import { computed, ref, watchEffect, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Modal, message } from 'ant-design-vue'
import { DeleteOutlined, ExclamationCircleOutlined, WarningOutlined, RedoOutlined,PushpinOutlined} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import '../styles/task-group-card.css'
import TaskModal from '../components/TaskModal.vue'
import { addTask, deleteTask, restoreTask, updateTask, normalizeTask, pinTask, unpinTask } from '../api/tasks'

const deleteTimers = new Map()
const props = defineProps({
  title: { type: String, required: true },
  color: { type: String, default: 'blue' }, // red | yellow | blue | green
  initialItems: { type: Array, default: () => [] },
  taskLevel: { type: Number, required: true },
})

const emit = defineEmits(['reload'])
const router = useRouter()

const peopleOptions = [
  { label: 'Lucia', value: 'Lucia' },
  { label: 'Simon', value: 'Simon' },
  { label: 'Susie', value: 'Susie' },
  { label: 'Shiro', value: 'shiro' },
]

const task_info = ref([])
watchEffect(() => {
  task_info.value = sortPinnedFirst((props.initialItems || []).map(x => ({
    ...x,
    pinned: Boolean(x.pinned),
    pendingDelete: false,
    deleting: false,
  })))
})

const palette = {
  red: {
    header: '#ef4444',
    body: 'rgba(239, 68, 68, 0.08)',
    shadow: 'rgba(239, 68, 68, 0.15)',
  },
  yellow: {
    header: '#f59e0b',
    body: 'rgba(245, 158, 11, 0.08)',
    shadow: 'rgba(245, 158, 11, 0.15)',
  },
  blue: {
    header: '#3b82f6',
    body: 'rgba(59, 130, 246, 0.08)',
    shadow: 'rgba(59, 130, 246, 0.15)',
  },
  green: {
    header: '#10b981',
    body: 'rgba(16, 185, 129, 0.08)',
    shadow: 'rgba(16, 185, 129, 0.15)',
  },
}

const headerStyle = computed(() => {
  const p = palette[props.color] || palette.blue
  return {
    background: p.header,
  }
})

const cardStyle = computed(() => {
  const p = palette[props.color] || palette.blue
  return {
    boxShadow: `0 8px 20px ${p.shadow}`,
    border: `1px solid ${p.body}`,
  }
})

const open = ref(false)

function parseDueDate(value) {
  if (!value) return null

  const formats = [
    ['YYYY-MM-DD HH:mm', false],
    ['YYYY-MM-DD HH:mm:ss', false],
    ['YYYY-MM-DD', true],
  ]
  const parsed = formats
    .map(([f, isDateOnly]) => {
      const d = dayjs(value, f, true)
      return d.isValid() ? (isDateOnly ? d.startOf('day') : d) : null
    })
    .find(Boolean)

  if (parsed) return parsed
  const flexible = dayjs(value)
  if (flexible.isValid()) return flexible

  return null
}

function formatRemaining(diffMinutes) {
  const days = Math.floor(diffMinutes / (24 * 60))
  const hours = Math.floor((diffMinutes % (24 * 60)) / 60)
  const minutes = diffMinutes % 60

  if (days > 0) return `In ${days}d ${hours ? hours + 'h' : ''}`
  if (hours > 0) return `In ${hours}h ${minutes ? minutes + 'm' : ''}`
  return `In ${minutes}m`
}

function canComplete(dueDateStr) {
  return getDueStatus(dueDateStr) !== 'overdue'
}


function dueText(dueDateStr) {
  if (!dueDateStr) return ''

  const due = parseDueDate(dueDateStr)
  if (!due) return ''

  const diffMinutes = due.diff(dayjs(), 'minute')
  const displayText = due.format('YYYY-MM-DD HH:mm')

  if (diffMinutes < 0) {
    return `${displayText} · Overdue`
  }

  return `${displayText} · ${formatRemaining(diffMinutes)}`
}

async function remove(id) {
  const DELETE_MODAL_TITLE = 'Delete Task'
  const DELETE_MODAL_CONTENT = 'Do you want to delete this task?'
  const DELETE_OK_TEXT = 'Delete'
  const DELETE_CANCEL_TEXT = 'Cancel'
  const DELETE_DELAY_MS = 5000
  const DELETE_UNDO_MESSAGE = 'Task will be deleted in 5 seconds. Click redo to undo.'
  Modal.confirm({
    title: DELETE_MODAL_TITLE,
    content: DELETE_MODAL_CONTENT,
    okText: DELETE_OK_TEXT,
    cancelText: DELETE_CANCEL_TEXT,
    onOk: async () => {
      const task = task_info.value.find(x => x.id === id)
      if (!task) return
      try {
        await deleteTask(id)
        task.pendingDelete = true
        task.deleting = false
        message.info(DELETE_UNDO_MESSAGE)
        const timer = setTimeout(() => {
          try {
            if (localStorage.getItem('authGuest')) {
              const raw = localStorage.getItem('guest_tasks')
              const g = raw ? JSON.parse(raw) : []
              const remaining = g.filter(t => Number(t.id) !== Number(id))
              if (remaining.length > 0) localStorage.setItem('guest_tasks', JSON.stringify(remaining))
              else localStorage.removeItem('guest_tasks')
            }
          } catch (err) {
            console.error('Failed to update guest_tasks in localStorage', err)
          }

          task_info.value = task_info.value.filter(x => x.id !== id)
          deleteTimers.delete(id)
          emit('reload')
        }, DELETE_DELAY_MS)
        deleteTimers.set(id, timer)
      } catch (e) {
        console.error(e)
        message.error(e?.message || 'Failed to delete task.')
      }
    }
  })
}

async function undoRemove(id) {
  const task = task_info.value.find(x => x.id === id)
  if (!task) return

  const timer = deleteTimers.get(id)
  if (timer) {
    clearTimeout(timer)
    deleteTimers.delete(id)
  }
  try {
    await restoreTask(id)
    task.pendingDelete = false
    task.deleting = false
    message.success('Task deletion undone.')
  } catch (e) {
    console.error(e)
    message.error(e?.message || 'Failed to restore task.')
  }
}

const modalMode = ref('add') // 'add' | 'edit'
const editingTask = ref(null)

function showAddDialog() {
  const isGuest = !!localStorage.getItem('authGuest')
  if (isGuest) {
    let guestTasks = []
    try {
      const raw = localStorage.getItem('guest_tasks')
      guestTasks = raw ? JSON.parse(raw) : []
    } catch (err) {
      guestTasks = []
    }
    const GUEST_LIMIT = 8
    if (guestTasks.length >= GUEST_LIMIT) {
      Modal.confirm({
        title: 'Guest task limit reached',
        content: 'You have reached the 8-task limit for guest accounts. Please login to create more tasks.',
        okText: 'Login',
        cancelText: 'Cancel',
        onOk: () => {
          localStorage.removeItem('authGuest')
          router.push({ path: '/auth', query: { mode: 'login' } })
        },
      })
      return
    }
  }

  modalMode.value = 'add'
  editingTask.value = null
  open.value = true
}

function showEditDialog(item) {
  modalMode.value = 'edit'
  editingTask.value = { ...item }
  open.value = true
}

//Set default due date 
const TASK_DUE_SUBMIT_DEFAULT = 6
function setDefaultDueDate(dueDate) {
  return dueDate
    ? dayjs(dueDate).add(TASK_DUE_SUBMIT_DEFAULT, 'minute').format('YYYY-MM-DD HH:mm')
    : null
}


async function handleSubmit(payload) {
  if (payload.mode === 'add') {
    try {
      const t = await addTask({
        task_title: payload.title,
        task_due: setDefaultDueDate(payload.dueDate),
        task_level: props.taskLevel
      })
      const normalized = normalizeTask(t)
      if (normalized.task_level === null) {
        console.log('Invalid task! Please check database.')
        return
      }
      const newTask = {
        ...normalized,
        pinned: Boolean(normalized.pinned),
        pendingDelete: false,
        deleting: false,
      }
      task_info.value = sortPinnedFirst(task_info.value)
      task_info.value.unshift(newTask)
      message.success('Task created successfully.')
    } catch (e) {
      console.error(e)
      message.error(e?.message || 'Failed to create task. Please try again later.')
    }
    return
  }

  if (payload.mode === 'edit') {
    try {
      const t = await updateTask(payload.id, {
        task_title: payload.title,
        task_due: setDefaultDueDate(payload.dueDate),
      })
      const normalized = normalizeTask(t)
      const index = task_info.value.findIndex(x => x.id === normalized.id)
      if (index !== -1) {
        task_info.value[index] = {
          ...task_info.value[index],
          ...normalized,
        }
        message.success('Task updated successfully.')
      }
    } catch (e) {
      console.error(e)
      message.error(e?.message || 'Failed to update task.')
    }
    return
  }
}


function getDueStatus(dueDateStr) {
  if (!dueDateStr) return 'normal'

  const now = dayjs()
  const due = parseDueDate(dueDateStr)
  if (!due) return 'normal'

  const diffMinutes = due.diff(now, 'minute')

  if (diffMinutes < 0) return 'overdue'
  if (diffMinutes <= 3 * 24 * 60) return 'warning'
  return 'normal'
}

function dueTooltip(dueDateStr) {
  if (!dueDateStr) return ''

  const now = dayjs()
  const due = parseDueDate(dueDateStr)
  if (!due) return ''

  const diffMinutes = due.diff(now, 'minute')

  if (diffMinutes < 0) {
    const overdueMinutes = Math.abs(diffMinutes)
    const days = Math.floor(overdueMinutes / (24 * 60))
    const hours = Math.floor((overdueMinutes % (24 * 60)) / 60)
    const minutes = overdueMinutes % 60

    if (days > 0) return `Overdue ${days} day ${hours} hours ${minutes} minutes`
    if (hours > 0) return `Overdue ${hours} hours ${minutes} minutes`
    return `Overdue ${minutes} minutes`
  }

  if (diffMinutes <= 3 * 24 * 60) {
    return formatRemaining(diffMinutes)
  }

  return ''
}

async function toggleDone(item, checked) {
  const prevDone = item.done
  item.done = checked
  try {
    await updateTask(item.id, { is_finished: checked ? 1 : 0 })
    message.success('Task status updated.')
  } catch (e) {
    item.done = prevDone
    console.error(e)
    message.error(e?.message || 'Failed to update task status.')
  }
}

function sortPinnedFirst(items = []) {
  return [...items].sort((a, b) => Number(Boolean(b.pinned)) - Number(Boolean(a.pinned)))
}

async function togglePin(item) {
  if (!item || item.pendingDelete) return
  try {
    if (item.pinned) {
      await unpinTask(item.id)
      message.success('Task unpinned.')
    } else {
      await pinTask(item.id)
      message.success('Task pinned.')
    }
    emit('reload')
  } catch (e) {
    console.error(e)
    message.error('Failed to update pin status.')
  }
}


onBeforeUnmount(() => {
  for (const t of deleteTimers.values()) {
    clearTimeout(t)
  }
  deleteTimers.clear()
})
</script>
