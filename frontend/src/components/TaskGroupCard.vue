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
                v-model:checked="item.done" />
              <div class="text">
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

              <a-button type="text" :class="{ invisible: item.pendingDelete }" @click="showEditDialog(item)">
                <EditOutlined />
              </a-button>

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
import { computed, ref, watchEffect } from 'vue'
import { Modal, message } from 'ant-design-vue'
import { DeleteOutlined, ExclamationCircleOutlined, EditOutlined, WarningOutlined, RedoOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import '../styles/task-group-card.css'
import TaskModal from '../components/TaskModal.vue'
import { addTask, deleteTask, normalizeTask } from '../api/tasks'

const deleteTimers = new Map()
const props = defineProps({
  title: { type: String, required: true },
  color: { type: String, default: 'blue' }, // red | yellow | blue | green
  initialItems: { type: Array, default: () => [] },
  taskLevel: { type: Number, required: true },
})

const emit = defineEmits(['reload'])

const peopleOptions = [
  { label: 'Lucia', value: 'Lucia' },
  { label: 'Simon', value: 'Simon' },
  { label: 'Susie', value: 'Susie' },
  { label: 'Shiro', value: 'shiro' },
]

const task_info = ref([])
watchEffect(() => {
  task_info.value = (props.initialItems || []).map(x => ({
    ...x,
    pendingDelete: false,
    deleting: false,
  }))
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

function canComplete(dueDateStr) {
  return getDueStatus(dueDateStr) !== 'overdue'
}


function dueText(dueDateStr) {
  if (!dueDateStr) return ''

  const today = dayjs().startOf('day')
  const due = dayjs(dueDateStr, 'YYYY-MM-DD').startOf('day')
  const diff = due.diff(today, 'day')

  if (diff === 0) return `${dueDateStr} · Due today`
  if (diff > 0) return `${dueDateStr} · Due in ${diff} days`
  return `${dueDateStr} · Overdue ${Math.abs(diff)} days`
}

function remove(id) {
  Modal.confirm({
    title: 'Delete Task',
    content: 'Do you want to delete this task?',
    okText: 'Delete',
    cancelText: 'Cancel',
    onOk: () => {
      const task = task_info.value.find(x => x.id === id)
      if (!task) return

      task.pendingDelete = true
      message.info('Task will be deleted in 5 seconds. Click redo to undo.')

      const timer = setTimeout(() => {
        finalizeRemove(id)
      }, 5000)

      deleteTimers.set(id, timer)
    }
  })
}

function undoRemove(id) {
  const task = task_info.value.find(x => x.id === id)
  if (!task) return

  const timer = deleteTimers.get(id)
  if (timer) {
    clearTimeout(timer)
    deleteTimers.delete(id)
  }

  task.pendingDelete = false
  task.deleting = false
  message.success('Task deletion undone.')
}

async function finalizeRemove(id) {
  const task = task_info.value.find(x => x.id === id)
  if (!task) return

  task.deleting = true

  setTimeout(async () => {
    try {
      await deleteTask(id)
      task_info.value = task_info.value.filter(x => x.id !== id)
      deleteTimers.delete(id)
      emit('reload')
      message.success('Task deleted successfully.')
    } catch (e) {
      console.error(e)

      task.deleting = false
      task.pendingDelete = false
      deleteTimers.delete(id)

      message.error('Failed to delete task. Please try again later.')
    }
  }, 400)
}

const modalMode = ref('add') // 'add' | 'edit'
const editingTask = ref(null)

function showAddDialog() {
  modalMode.value = 'add'
  editingTask.value = null
  open.value = true
}

function showEditDialog(item) {
  modalMode.value = 'edit'
  editingTask.value = { ...item }
  open.value = true
}

async function handleSubmit(payload) {
  if (payload.mode === 'add') {
    try {
      const t = await addTask({
        task_title: payload.title,
        task_due: payload.dueDate || null,
        task_level: props.taskLevel
      })
      const normalized = normalizeTask(t)
      if (normalized.task_level === null) {
        message.error('Network error. Please try creating the task again.')
        return
      }

      const newTask = {
        ...normalized,
        pendingDelete: false,
        deleting: false,
      }

      task_info.value.unshift(newTask)
      message.success('Task created successfully.')
    } catch (e) {
      console.error(e)
      message.error('Failed to create task. Please try again later.')
    }
    return
  }
}

function getDueStatus(dueDateStr) {
  if (!dueDateStr) return 'normal'

  const today = dayjs().startOf('day')
  const due = dayjs(dueDateStr, 'YYYY-MM-DD').startOf('day')
  const diff = due.diff(today, 'day')

  if (diff < 0) return 'overdue'
  if (diff <= 3) return 'warning'
  return 'normal'
}

function dueTooltip(dueDateStr) {
  if (!dueDateStr) return ''

  const today = dayjs().startOf('day')
  const due = dayjs(dueDateStr, 'YYYY-MM-DD').startOf('day')
  const diff = due.diff(today, 'day')

  if (diff < 0) return `Overdue ${Math.abs(diff)} day(s)`
  if (diff <= 3) return `Due in ${diff} day(s)`
  return ''
}

</script>
