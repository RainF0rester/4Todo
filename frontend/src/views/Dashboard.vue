<template>
  <a-card title="Dashboard" class="dashboard-card">
    <div class="dashboard-filter">
      <a-segmented v-model:value="statusFilter" :options="segmentedOptions" />
    </div>
    <div class="dashboard-filter-row">
      <a-radio-group v-model:value="periodFilter">
        <a-radio v-for="option in periodOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </a-radio>
      </a-radio-group>
    </div>

    <div class="dashboard-summary">
      <div class="summary-item">
        <div class="summary-label">Filtered tasks</div>
        <div class="summary-count">{{ filteredTasks.length }}</div>
      </div>
      <div class="summary-item">
        <div class="summary-label">Total tasks</div>
        <div class="summary-count">{{ counts.all }}</div>
      </div>
    </div>

    <div class="dashboard-body">
      <p class="dashboard-note">Showing <strong>{{ selectedLabel }}</strong> tasks.</p>
      <a-list :data-source="filteredTasks" bordered size="small" class="dashboard-list" :pagination="paginationConfig">
        <template #renderItem="{ item }">
          <a-list-item>
            <div class="item-content">
              <span class="item-title">{{ item.title }}</span>
              <span class="item-meta">{{ item.dueDate || 'No due date' }}</span>
            </div>
          </a-list-item>
        </template>
      </a-list>
    </div>
  </a-card>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import dayjs from 'dayjs'
import { CalendarOutlined, CheckCircleOutlined, FlagOutlined } from '@ant-design/icons-vue'
import { Radio as ARadio, RadioGroup as ARadioGroup } from 'ant-design-vue'
import { getTaskList } from '../api/tasks'

const tasks = ref([])
const statusFilter = ref('all')
const periodFilter = ref('daily')

const counts = computed(() => ({
  all: tasks.value.length,
  completed: tasks.value.filter((task) => task.done).length,
  flagged: tasks.value.filter((task) => Number(task.task_level) >= 3).length,
}))

const filteredTasks = computed(() => {
  const now = dayjs()
  let result = tasks.value

  switch (statusFilter.value) {
    case 'completed':
      result = result.filter((task) => task.done)
      break
    case 'flagged':
      result = result.filter((task) => Number(task.task_level) >= 3)
      break
    default:
      break
  }

  if (periodFilter.value !== 'daily') {
    result = result.filter((task) => {
      if (!task.dueDate) return false
      const due = dayjs(task.dueDate)
      if (!due.isValid()) return false
      switch (periodFilter.value) {
        case 'daily':
          return due.isSame(now, 'day')
        case 'weekly':
          return due.isSame(now, 'week')
        case 'monthly':
          return due.isSame(now, 'month')
        case 'quarterly':
          return due.quarter() === now.quarter() && due.isSame(now, 'year')
        case 'yearly':
          return due.isSame(now, 'year')
      }
      return true
    })
  } else {
    result = result.filter((task) => {
      if (!task.dueDate) return false
      const due = dayjs(task.dueDate)
      return due.isValid() && due.isSame(now, 'day')
    })
  }

  return result
})

const selectedLabel = computed(() => {
  const statusLabels = {
    all: 'All',
    completed: 'Completed',
    flagged: 'Flagged',
  }
  const periodLabels = {
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    quarterly: 'Quarterly',
    yearly: 'Yearly',
  }
  return `${statusLabels[statusFilter.value] || 'All'} / ${periodLabels[periodFilter.value]}`
})

const segmentedOptions = computed(() => [
  {
    label: h('span', { class: 'segment-label' }, [
      h(CalendarOutlined),
      h('span', { class: 'segment-text' }, ' All '),
      h('span', { class: 'segment-count' }, counts.value.all),
    ]),
    value: 'all',
  },
  {
    label: h('span', { class: 'segment-label' }, [
      h(CheckCircleOutlined),
      h('span', { class: 'segment-text' }, ' Completed '),
      h('span', { class: 'segment-count' }, counts.value.completed),
    ]),
    value: 'completed',
  },
  {
    label: h('span', { class: 'segment-label' }, [
      h(FlagOutlined),
      h('span', { class: 'segment-text' }, ' Flagged '),
      h('span', { class: 'segment-count' }, counts.value.flagged),
    ]),
    value: 'flagged',
  },
])
const periodOptions = computed(() => [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Quarterly', value: 'quarterly' },
  { label: 'Yearly', value: 'yearly' },
])

const paginationConfig = computed(() => filteredTasks.value.length > 20 ? { pageSize: 20 } : false)

async function loadTasks() {
  // TODO: get tasks from localstorage when guest login
  try {
    tasks.value = await getTaskList()
  } catch (err) {
    console.error('Unable to load tasks', err)
  }
}

onMounted(loadTasks)
</script>

<style scoped>
.dashboard-card {
  min-height: 100%;
}

.dashboard-filter {
  margin-bottom: 24px;
}

.dashboard-filter-row {
  margin-bottom: 16px;
}

.segment-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.segment-text {
  margin-left: 4px;
}

.segment-count {
  background: rgba(0, 0, 0, 0.06);
  border-radius: 50%;
  padding: 0 8px;
  font-size: 12px;
  width: 25px;
  height: 25px;
  line-height: 25px;
}

.dashboard-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.summary-item {
  flex: 1;
  padding: 16px;
  border-radius: 12px;
  background: #f5f7fb;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.summary-label {
  color: #6b7280;
}

.summary-count {
  font-size: 28px;
  font-weight: 700;
}

.dashboard-body {
  min-height: 240px;
}

.dashboard-note {
  margin-bottom: 16px;
}

.item-content {
  display: flex;
  justify-content: space-between;
  width: 100%;
  gap: 12px;
}

.item-title {
  font-weight: 600;
}

.item-meta {
  color: #6b7280;
}
</style>