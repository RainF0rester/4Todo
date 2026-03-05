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
          <a-list-item class="row">
            <div class="left">
              <a-checkbox :disabled="!canComplete(item.dueDate)" v-model:checked="item.done" />
              <div class="text">
                <div class="name" :class="{ done: item.done }" @click="showEditDialog(item)">
                  {{ item.title }}
                </div>
                <div v-if="item.dueDate" class="meta">{{ dueText(item.dueDate) }}</div>
              </div>
            </div>
            <div class="right">
              <a-tooltip v-if="!item.done && getDueStatus(item.dueDate) === 'overdue'" :title="dueTooltip(item.dueDate)"
                placement="top">
                <a-button type="text" class="overdue-btn">
                  <ExclamationCircleOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip v-else-if="getDueStatus(item.dueDate) === 'warning'" :title="dueTooltip(item.dueDate)"
                placement="top">
                <a-button type="text" class="warning-btn">
                  <WarningOutlined />
                </a-button>
              </a-tooltip>
              <a-button type="text" @click="showEditDialog(item)">
                <EditOutlined />
              </a-button>
              <a-button type="text" danger @click="remove(item.id)">
                <DeleteOutlined />
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
import { DeleteOutlined, ExclamationCircleOutlined, EditOutlined, WarningOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import '../styles/task-group-card.css'
import TaskModal from '../components/TaskModal.vue'
import { addTask } from '../api/tasks'


const props = defineProps({
  title: { type: String, required: true },
  color: { type: String, default: 'blue' }, // red | yellow | blue | green
  initialItems: { type: Array, default: () => [] },
  taskLevel: { type: Number, default: 0 },
})

const peopleOptions = [
  { label: 'Lucia', value: 'Lucia' },
  { label: 'Simon', value: 'Simon' },
  { label: 'Susie', value: 'Susie' },
  { label: 'Shiro', value: 'shiro' },
]

const task_info = ref([])
watchEffect(() => {
  task_info.value = (props.initialItems || []).map(x => ({ ...x }))
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
  task_info.value = task_info.value.filter(x => x.id !== id)
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
  if(payload.mode === 'add'){
    try {
      const t = await addTask({
        task_title: payload.title,
        task_due: payload.dueDate || null,
        task_level: props.taskLevel,
      })
      const newTask = {
        id: t.id,
        title: t.task_title,
        dueDate:t.task_due ? t.task_due : '',
        done: t.is_finished ? true : false,
        task_level: t.task_level != null ? t.task_level : 0,
      }
      task_info.value.unshift(newTask)
    }catch (e) {
      console.error(e)
    }
    return
}}

  
// function handleSubmit(payload) {
//   if (payload.mode === 'add') {
//     task_info.value.unshift({
//       id: Date.now(),
//       title: payload.title,
//       dueDate: payload.dueDate,
//       assignee: payload.assignee,
//       done: false,
//     })
//     return
//   }

//   // edit
//   const idx = task_info.value.findIndex(x => x.id === payload.id)
//   if (idx !== -1) {
//     task_info.value[idx] = {
//       ...task_info.value[idx],
//       title: payload.title,
//       dueDate: payload.dueDate,
//       assignee: payload.assignee,
//     }
//   }
// }

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
